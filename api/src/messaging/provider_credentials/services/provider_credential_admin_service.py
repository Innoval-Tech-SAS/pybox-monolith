import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.security.services.encrypt_service import encrypt_service
from messaging.provider_credentials.models.provider_credential_model import (
    MessagingProviderCredentialModel,
)
from messaging.provider_credentials.repository.provider_credential_repository import (
    MessagingProviderCredentialRepository,
)
from messaging.provider_credentials.schemas.provider_credential_schemas import (
    MessagingProviderCredentialResponse,
    MessagingProviderCredentialUpsert,
)


class MessagingProviderCredentialAdminService:
    """Administración de credenciales de mensajería (solo ADMIN GLOBAL). Cifra los
    secretos al escribir y NUNCA los devuelve descifrados."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = MessagingProviderCredentialRepository(session)

    async def list(self) -> list[MessagingProviderCredentialResponse]:
        rows = await self._repo.list_all()
        return [self._to_response(row) for row in rows]

    async def upsert(
        self, data: MessagingProviderCredentialUpsert
    ) -> MessagingProviderCredentialResponse:
        # Solo se cifran los secretos con valor: un secreto vacío no se toca (permite
        # editar public_config/lookup_key sin reenviar los secretos ya guardados).
        encrypted = {
            key: encrypt_service.encrypt_to_str(value)
            for key, value in data.secrets.items()
            if value
        }
        existing = await self._repo.get(data.country_code, data.provider)
        if existing is None:
            row = MessagingProviderCredentialModel(
                country_code=data.country_code,
                provider=data.provider,
                secrets=encrypted,
                public_config=data.public_config,
                lookup_key=data.lookup_key,
                is_active=data.is_active,
            )
            saved = await self._repo.add(row)
        else:
            # Merge de secretos: los enviados rotan; los omitidos se conservan.
            existing.secrets = {**(existing.secrets or {}), **encrypted}
            existing.public_config = data.public_config
            existing.lookup_key = data.lookup_key
            existing.is_active = data.is_active
            saved = await self._repo.update(existing)
        return self._to_response(saved)

    async def delete(self, credential_id: uuid.UUID) -> None:
        row = await self._repo.get_by_id(credential_id)
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Credencial no encontrada")
        await self._repo.delete(row)

    async def restore(
        self, credential_id: uuid.UUID
    ) -> MessagingProviderCredentialResponse:
        row = await self._repo.get_by_id_including_deleted(credential_id)
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Credencial no encontrada")
        restored = await self._repo.restore(row)
        return self._to_response(restored)

    @staticmethod
    def _to_response(
        row: MessagingProviderCredentialModel,
    ) -> MessagingProviderCredentialResponse:
        return MessagingProviderCredentialResponse(
            id=row.id,
            country_code=row.country_code,
            provider=row.provider,
            public_config=row.public_config or {},
            secret_keys=sorted((row.secrets or {}).keys()),
            lookup_key=row.lookup_key,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
