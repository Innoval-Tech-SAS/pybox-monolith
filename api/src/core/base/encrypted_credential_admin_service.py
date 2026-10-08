"""Service base genérico para el CRUD admin de credenciales cifradas de proveedor."""

import uuid
from typing import Generic, Optional, Protocol, Type, TypeVar

from fastapi import HTTPException, status

from core.base.encrypted_credential_model import EncryptedCredentialModel
from core.base.encrypted_credential_schemas import (
    EncryptedCredentialResponseBase,
    EncryptedCredentialUpsertBase,
)
from core.security.services.encrypt_service import encrypt_service

ModelT = TypeVar("ModelT", bound=EncryptedCredentialModel)
UpsertT = TypeVar("UpsertT", bound=EncryptedCredentialUpsertBase)
ResponseT = TypeVar("ResponseT", bound=EncryptedCredentialResponseBase)


class _CredentialRepositoryProtocol(Protocol[ModelT]):
    """Forma mínima de repository que necesita el service base: la que ya cumplen
    `PlatformGatewayCredentialRepository` y `MessagingProviderCredentialRepository`
    (`CountryScopedCredentialRepositoryMixin` + `SoftDeleteRepositoryBase`)."""

    async def list_all(self) -> list[ModelT]: ...

    async def get(
        self, country_code: Optional[str], provider: object
    ) -> Optional[ModelT]: ...

    async def add(self, instance: ModelT) -> ModelT: ...

    async def update(self, instance: ModelT) -> ModelT: ...

    async def get_by_id(self, id: object) -> Optional[ModelT]: ...

    async def get_by_id_including_deleted(self, id: object) -> Optional[ModelT]: ...

    async def delete(self, instance: ModelT) -> ModelT: ...

    async def restore(self, instance: ModelT) -> ModelT: ...


class EncryptedCredentialAdminServiceBase(Generic[ModelT, UpsertT, ResponseT]):
    """CRUD admin común a las credenciales cifradas de proveedor externo (solo ADMIN
    GLOBAL): cifra los secretos al escribir y NUNCA los devuelve descifrados.

    Compartido por `billing.provider_credentials` y `messaging.provider_credentials`
    (ambas con alcance `country_code`, NULL = global). `receivables.payment_gateways`
    no hereda de esta base: su alcance es `organization_id` obligatorio sin fallback
    global y su contrato es distinto (`create`/`update` con conflicto 409 en vez de
    upsert) — ver `PaymentGatewayCredentialManagementService`.
    """

    model_class: Type[ModelT]
    response_class: Type[ResponseT]

    def __init__(self, repo: _CredentialRepositoryProtocol[ModelT]) -> None:
        self._repo = repo

    async def list(self) -> list[ResponseT]:
        rows = await self._repo.list_all()
        return [self._to_response(row) for row in rows]

    async def upsert(self, data: UpsertT) -> ResponseT:
        # Solo se cifran los secretos con valor: un secreto vacío no se toca (permite
        # editar public_config/lookup_key sin reenviar los secretos ya guardados).
        encrypted = {
            key: encrypt_service.encrypt_to_str(value)
            for key, value in data.secrets.items()
            if value
        }
        existing = await self._repo.get(
            data.country_code, data.provider  # type: ignore[attr-defined]
        )
        if existing is None:
            row = self.model_class(
                country_code=data.country_code,  # type: ignore[attr-defined]
                provider=data.provider,  # type: ignore[attr-defined]
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

    async def restore(self, credential_id: uuid.UUID) -> ResponseT:
        row = await self._repo.get_by_id_including_deleted(credential_id)
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Credencial no encontrada")
        restored = await self._repo.restore(row)
        return self._to_response(restored)

    def _to_response(self, row: ModelT) -> ResponseT:
        return self.response_class(
            id=row.id,
            country_code=row.country_code,  # type: ignore[attr-defined]
            provider=row.provider,  # type: ignore[attr-defined]
            public_config=row.public_config or {},
            secret_keys=sorted((row.secrets or {}).keys()),
            lookup_key=row.lookup_key,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
