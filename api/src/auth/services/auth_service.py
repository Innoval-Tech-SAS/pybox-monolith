from typing import cast

from flask import g, has_request_context, session

from auth.enums.auth_enums import AuthProvider
from users.repository.user_repository import UserRepository
from users.models.user_model import UserModel
from security.services.auth_token_service import AuthTokenService
from security.services.password_hasher_service import PasswordHasherService
from ..schemas.auth_schemas import AuthResult, ProviderLogin, UserCreate, UserLogin
from .oauth_provider_service import OAuthProviderService, ProviderProfile
from ..utils.auth_utils import (
    normalize_email,
    normalize_optional,
    require_value,
    resolve_auth_provider,
    resolve_document_type,
)


class AuthService:

    def __init__(
        self,
        user_repository: UserRepository = UserRepository(),
        password_hasher: PasswordHasherService = PasswordHasherService(),
        token_service: AuthTokenService | None = None,
        oauth_provider_service: OAuthProviderService = OAuthProviderService(),
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_service = token_service
        self.oauth_provider_service = oauth_provider_service

    def register_user(self, user_data: UserCreate) -> UserModel:
        email = normalize_email(user_data["email"])
        phone_number = require_value(
            user_data["phone_number"],
            "El número de teléfono es obligatorio.",
        )
        document_type = resolve_document_type(user_data["document_type"])
        document_number = require_value(
            user_data["document_number"],
            "El número de documento es obligatorio.",
        )

        if self.user_repository.get_by_email(email):
            raise ValueError("El correo electrónico ya está registrado.")

        if phone_number and self.user_repository.get_by_phone_number(phone_number):
            raise ValueError("El número de teléfono ya está registrado.")

        if self.user_repository.get_by_document(document_type, document_number):
            raise ValueError("El documento ya está registrado.")

        user = UserModel(
            firstname=require_value(
                user_data["firstname"],
                "El nombre es obligatorio.",
            ),
            lastname=require_value(
                user_data["lastname"],
                "El apellido es obligatorio.",
            ),
            email=email,
            hashed_password=self.password_hasher.hash_password(user_data["password"]),
            phone_number=phone_number,
            auth_provider=AuthProvider.SELF,
            document_type=document_type,
            document_number=document_number,
        )

        return self.user_repository.add(user)

    def authenticate_user(self, user_data: UserLogin) -> AuthResult:

        email = normalize_email(user_data["email"])
        password = require_value(
            user_data["password"],
            "La contraseña es obligatoria.",
        )

        user = self.user_repository.get_by_email(email)

        if not user:
            raise ValueError("Credenciales inválidas.")

        stored_hash = cast(str | None, user.hashed_password)
        if not stored_hash:
            raise ValueError("Este usuario debe autenticarse con proveedor externo.")

        is_valid, new_hash = self.password_hasher.verify_and_maybe_rehash(
            stored_hash,
            password,
        )

        if not is_valid:
            raise ValueError("Credenciales inválidas.")

        if new_hash:
            setattr(user, "hashed_password", new_hash)
            user = self.user_repository.update(user)

        return self._open_session(user, AuthProvider.SELF)

    def authenticate_provider_user(self, provider_data: ProviderLogin) -> AuthResult:
        provider = resolve_auth_provider(provider_data["provider"])
        token = require_value(provider_data["token"], "El token es obligatorio.")

        if provider == AuthProvider.SELF:
            raise ValueError("SELF no es un proveedor externo.")

        provider_profile = self.oauth_provider_service.verify_provider_token(
            provider,
            token,
        )
        user = self._get_or_create_provider_user(provider_profile, provider_data)

        return self._open_session(user, provider)

    def verify_access_token(self, token: str) -> dict:
        return self._get_token_service().verify_token(token)

    def close_session(self):
        if not has_request_context():
            return

        user = getattr(g, "current_user", None)
        if user:
            setattr(user, "is_active_sessions", False)
            self.user_repository.update(user)

        session.clear()
        g.current_user = None
        g.access_token = None

    def _get_or_create_provider_user(
        self,
        provider_profile: ProviderProfile,
        provider_data: ProviderLogin,
    ) -> UserModel:
        user = self.user_repository.get_by_provider_identity(
            provider_profile.provider,
            provider_profile.provider_user_id,
        )

        if user:
            return user

        user = self.user_repository.get_by_email(provider_profile.email)
        if user:
            setattr(user, "auth_provider", provider_profile.provider)
            setattr(user, "provider_user_id", provider_profile.provider_user_id)
            return self.user_repository.update(user)

        user = UserModel(
            firstname=self._provider_value(
                provider_data,
                "firstname",
                provider_profile.firstname,
                "El nombre es obligatorio.",
            ),
            lastname=self._provider_value(
                provider_data,
                "lastname",
                provider_profile.lastname,
                "El apellido es obligatorio.",
            ),
            email=provider_profile.email,
            hashed_password=None,
            phone_number=require_value(
                provider_data["phone_number"],
                "El número de teléfono es obligatorio.",
            ),
            auth_provider=provider_profile.provider,
            provider_user_id=provider_profile.provider_user_id,
            document_type=resolve_document_type(provider_data["document_type"]),
            document_number=require_value(
                provider_data["document_number"],
                "El número de documento es obligatorio.",
            ),
        )

        return self.user_repository.add(user)

    def _open_session(self, user: UserModel, auth_provider: AuthProvider) -> AuthResult:
        setattr(user, "is_active_sessions", True)
        user = self.user_repository.update(user)

        access_token = self._get_token_service().generate_token(user, auth_provider)

        if has_request_context():
            session["user_id"] = str(user.id)
            session["email"] = str(user.email)
            session["auth_provider"] = auth_provider.value
            session["access_token"] = access_token
            g.current_user = user
            g.access_token = access_token

        return {
            "user": user,
            "access_token": access_token,
            "token_type": "Bearer",
            "auth_provider": auth_provider,
        }

    def _get_token_service(self) -> AuthTokenService:
        if self.token_service is None:
            self.token_service = AuthTokenService()

        return self.token_service

    def _provider_value(
        self,
        provider_data: ProviderLogin,
        key: str,
        fallback: str | None,
        message: str,
    ) -> str:
        value = normalize_optional(provider_data.get(key)) or fallback
        return require_value(value or "", message)
