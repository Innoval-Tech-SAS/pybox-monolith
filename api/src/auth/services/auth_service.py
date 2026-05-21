from typing import cast

import jwt

from auth.enums.auth_enums import AuthProvider
from users.repository.user_repository import UserRepository
from users.repository.role_assignment_repository import RoleAssignmentRepository
from users.models.user_model import UserModel
from users.models.role_assignment_model import RoleAssignmentModel
from users.enums.user_enums import UserRole, UserScope
from security.services.auth_token_service import AuthTokenService
from security.services.password_hasher_service import PasswordHasherService
from ..schemas.auth_schemas import (
    AuthResponse,
    ProviderAuth,
    ProviderLogin,
    UserCreate,
    UserLogin,
)
from .oauth_provider_service import OAuthProviderService, ProviderProfile
from ..utils.auth_utils import (
    normalize_email,
    normalize_optional,
    require_value,
    resolve_auth_provider,
    resolve_document_type,
    resolve_nationality,
)


class AuthService:

    def __init__(
        self,
        user_repository: UserRepository,
        role_assignment_repository: RoleAssignmentRepository,
        password_hasher: PasswordHasherService | None = None,
        token_service: AuthTokenService | None = None,
        oauth_provider_service: OAuthProviderService | None = None,
    ):
        self.user_repository = user_repository
        self.role_assignment_repository = role_assignment_repository
        self.password_hasher = password_hasher or PasswordHasherService()
        self.token_service = token_service or AuthTokenService()
        self.oauth_provider_service = oauth_provider_service or OAuthProviderService()

    async def register_and_authenticate(
        self, user_data: UserCreate, role: UserRole, scope: UserScope
    ) -> AuthResponse:
        user = await self.register_user(user_data)
        await self.role_assignment_repository.add(
            RoleAssignmentModel(user_id=cast(int, user.id), role=role, scope=scope)
        )
        return await self._build_response(user, AuthProvider.SELF)

    async def register_user(self, user_data: UserCreate) -> UserModel:
        email = normalize_email(user_data.email)
        phone_number = require_value(
            user_data.phone_number, "El número de teléfono es obligatorio."
        )
        nationality = resolve_nationality(user_data.nationality)
        document_type = (
            resolve_document_type(user_data.document_type)
            if user_data.document_type
            else None
        )
        document_number = user_data.document_number or None

        if await self.user_repository.get_by_email(email):
            raise ValueError("El correo electrónico ya está registrado.")

        if await self.user_repository.get_by_phone_number(phone_number):
            raise ValueError("El número de teléfono ya está registrado.")

        if document_type and document_number:
            if await self.user_repository.get_by_document(
                document_type, document_number
            ):
                raise ValueError("El documento ya está registrado.")

        user = UserModel(
            firstname=require_value(user_data.firstname, "El nombre es obligatorio."),
            lastname=require_value(user_data.lastname, "El apellido es obligatorio."),
            email=email,
            hashed_password=self.password_hasher.hash_password(user_data.password),
            phone_number=phone_number,
            auth_provider=AuthProvider.SELF,
            nationality=nationality,
            document_type=document_type,
            document_number=document_number,
        )

        return await self.user_repository.add(user)

    async def authenticate_user(self, user_data: UserLogin) -> AuthResponse:
        email = normalize_email(user_data.email)
        password = require_value(user_data.password, "La contraseña es obligatoria.")

        user = await self.user_repository.get_by_email(email)
        if not user:
            raise ValueError("Credenciales inválidas.")

        stored_hash = cast(str | None, user.hashed_password)
        if not stored_hash:
            raise ValueError("Este usuario debe autenticarse con proveedor externo.")

        is_valid, new_hash = self.password_hasher.verify_and_maybe_rehash(
            stored_hash, password
        )
        if not is_valid:
            raise ValueError("Credenciales inválidas.")

        if new_hash:
            setattr(user, "hashed_password", new_hash)
            user = await self.user_repository.update(user)

        return await self._build_response(user, AuthProvider.SELF)

    async def authenticate_provider_user(
        self, provider_data: ProviderLogin
    ) -> AuthResponse:
        provider = resolve_auth_provider(provider_data.provider)
        token = require_value(str(provider_data.token), "El token es obligatorio.")

        if provider == AuthProvider.SELF:
            raise ValueError("SELF no es un proveedor externo.")

        provider_profile = self.oauth_provider_service.verify_provider_token(
            provider, token
        )
        user = await self._get_or_create_provider_user(provider_profile, provider_data)
        return await self._build_response(user, provider)

    async def authenticate_existing_provider_user(
        self, provider_data: ProviderAuth
    ) -> AuthResponse:
        provider = resolve_auth_provider(provider_data.provider)
        token = require_value(str(provider_data.token), "El token es obligatorio.")

        if provider == AuthProvider.SELF:
            raise ValueError("SELF no es un proveedor externo.")

        provider_profile = self.oauth_provider_service.verify_provider_token(
            provider, token
        )
        user = await self._get_provider_user_or_link_email(provider_profile)
        if not user:
            raise ValueError(
                "No encontramos una cuenta asociada a Google. Regístrate primero para completar tu perfil."
            )

        return await self._build_response(user, provider)

    async def refresh_tokens(self, refresh_token: str) -> AuthResponse:
        try:
            payload = jwt.decode(
                refresh_token,
                self.token_service.secret_key,
                algorithms=[self.token_service.ALGORITHM],
            )
        except jwt.ExpiredSignatureError as e:
            raise ValueError("El refresh token expiró.") from e
        except jwt.InvalidTokenError as e:
            raise ValueError("El refresh token no es válido.") from e

        user_id: int = payload["sub"]
        jti: str = payload["jti"]

        if not await self.token_service.verify_refresh_token(user_id, jti):
            raise ValueError("Sesión inválida o ya cerrada.")

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado.")

        await self.token_service.revoke_refresh_token(user_id)
        return await self._build_response(user, cast(AuthProvider, user.auth_provider))

    async def logout(self, user_id: int) -> None:
        await self.token_service.revoke_refresh_token(user_id)
        user = await self.user_repository.get_by_id(user_id)
        if user:
            setattr(user, "is_active_sessions", False)
            await self.user_repository.update(user)

    async def _get_or_create_provider_user(
        self,
        provider_profile: ProviderProfile,
        provider_data: ProviderLogin,
    ) -> UserModel:
        user = await self._get_provider_user_or_link_email(provider_profile)
        if user:
            return user

        phone_number = normalize_optional(provider_data.phone_number)
        nationality = (
            resolve_nationality(provider_data.nationality)
            if provider_data.nationality
            else None
        )

        if phone_number and await self.user_repository.get_by_phone_number(
            phone_number
        ):
            raise ValueError("El número de teléfono ya está registrado.")

        user = UserModel(
            firstname=(
                normalize_optional(provider_data.firstname)
                or normalize_optional(provider_profile.firstname)
                or provider_profile.email.split("@", 1)[0]
            ),
            lastname=(
                normalize_optional(provider_data.lastname)
                or normalize_optional(provider_profile.lastname)
                or ""
            ),
            email=provider_profile.email,
            hashed_password=None,
            phone_number=phone_number,
            auth_provider=provider_profile.provider,
            provider_user_id=provider_profile.provider_user_id,
            nationality=nationality,
            document_type=(
                resolve_document_type(provider_data.document_type)
                if provider_data.document_type
                else None
            ),
            document_number=provider_data.document_number or None,
        )
        return await self.user_repository.add(user)

    async def _get_provider_user_or_link_email(
        self,
        provider_profile: ProviderProfile,
    ) -> UserModel | None:
        user = await self.user_repository.get_by_provider_identity(
            provider_profile.provider,
            provider_profile.provider_user_id,
        )
        if user:
            return user

        user = await self.user_repository.get_by_email(provider_profile.email)
        if not user:
            return None

        setattr(user, "auth_provider", provider_profile.provider)
        setattr(user, "provider_user_id", provider_profile.provider_user_id)
        return await self.user_repository.update(user)

    async def _build_response(
        self, user: UserModel, auth_provider: AuthProvider
    ) -> AuthResponse:
        setattr(user, "is_active_sessions", True)
        await self.user_repository.update(user)
        access_token = self.token_service.generate_access_token(user, auth_provider)
        refresh_token = await self.token_service.generate_refresh_token(
            cast(int, user.id)
        )
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            auth_provider=auth_provider,
        )

    def _provider_value(
        self,
        provider_data: ProviderLogin,
        key: str,
        fallback: str | None,
        message: str,
    ) -> str:
        value = normalize_optional(getattr(provider_data, key, None)) or fallback
        return require_value(value or "", message)
