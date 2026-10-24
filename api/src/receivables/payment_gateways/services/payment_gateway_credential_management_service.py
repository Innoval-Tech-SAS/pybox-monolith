"""Alta, edición y borrado de credenciales de pasarela de cobro de una organización."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.security.services.encrypt_service import encrypt_service
from receivables.payment_gateways.models.payment_gateway_credential_model import (
    OrganizationGatewayCredentialModel,
)
from receivables.payment_gateways.repository.payment_gateway_credential_repository import (  # pylint: disable=line-too-long
    OrganizationGatewayCredentialRepository,
)
from receivables.payment_gateways.schemas.payment_gateway_credential_schemas import (
    OrganizationGatewayCredentialCreateRequest,
    OrganizationGatewayCredentialResponse,
    OrganizationGatewayCredentialUpdateRequest,
)


class OrganizationGatewayCredentialManagementService:
    """CRUD de las credenciales de pasarela de UNA organización, para que su propio
    ADMIN las gestione (ver `security_policies.require_org_admin` en el controller —
    más estricto que `payment_methods`, porque esto mueve dinero real de la empresa).

    Cifra los secretos al escribir y NUNCA los devuelve descifrados (mismo contrato que
    `messaging.provider_credentials`/`billing.provider_credentials`)."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = OrganizationGatewayCredentialRepository(session)

    async def list(
        self, organization_id: uuid.UUID
    ) -> list[OrganizationGatewayCredentialResponse]:
        rows = await self._repo.list_by_organization(organization_id)
        return [self._to_response(row) for row in rows]

    async def _get_owned(
        self, credential_id: uuid.UUID, organization_id: uuid.UUID
    ) -> OrganizationGatewayCredentialModel:
        row = await self._repo.get_by_id(credential_id)
        if row is None or row.organization_id != organization_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Credencial no encontrada")
        return row

    async def get(
        self, credential_id: uuid.UUID, organization_id: uuid.UUID
    ) -> OrganizationGatewayCredentialResponse:
        row = await self._get_owned(credential_id, organization_id)
        return self._to_response(row)

    async def create(
        self,
        organization_id: uuid.UUID,
        data: OrganizationGatewayCredentialCreateRequest,
    ) -> OrganizationGatewayCredentialResponse:
        existing = await self._repo.get_by_organization_and_provider(
            organization_id, data.provider
        )
        if existing is not None:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Ya existe una credencial de {data.provider.value} para esta "
                "organización — edítala en vez de crear otra.",
            )
        if data.is_active:
            # El checkout de autoservicio resuelve "la" pasarela activa de la
            # organización sin que el deudor elija (ver
            # `ReceivablesGatewayResolver.get_active_for_organization`) -- a lo sumo
            # una puede estarlo a la vez.
            await self._repo.deactivate_all(organization_id)
        row = OrganizationGatewayCredentialModel(
            organization_id=organization_id,
            provider=data.provider,
            secrets={
                key: encrypt_service.encrypt_to_str(value)
                for key, value in data.secrets.items()
                if value
            },
            public_config=data.public_config,
            lookup_key=data.lookup_key,
            is_active=data.is_active,
        )
        saved = await self._repo.add(row)
        return self._to_response(saved)

    async def update(
        self,
        credential_id: uuid.UUID,
        organization_id: uuid.UUID,
        data: OrganizationGatewayCredentialUpdateRequest,
    ) -> OrganizationGatewayCredentialResponse:
        row = await self._get_owned(credential_id, organization_id)
        if data.is_active:
            await self._repo.deactivate_all(organization_id, exclude_id=row.id)
        if data.secrets:
            # Merge de secretos: los enviados rotan; los omitidos se conservan (igual
            # contrato que las otras dos tablas de credenciales del proyecto).
            encrypted = {
                key: encrypt_service.encrypt_to_str(value)
                for key, value in data.secrets.items()
                if value
            }
            row.secrets = {**(row.secrets or {}), **encrypted}
        if data.public_config is not None:
            row.public_config = data.public_config
        if data.lookup_key is not None:
            row.lookup_key = data.lookup_key
        if data.is_active is not None:
            row.is_active = data.is_active
        saved = await self._repo.update(row)
        return self._to_response(saved)

    async def delete(
        self, credential_id: uuid.UUID, organization_id: uuid.UUID
    ) -> None:
        row = await self._get_owned(credential_id, organization_id)
        await self._repo.delete(row)

    async def restore(
        self, credential_id: uuid.UUID
    ) -> OrganizationGatewayCredentialResponse:
        """Solo Admin Global: sin scope de organización, ya autorizado por policy."""
        row = await self._repo.get_by_id_including_deleted(credential_id)
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Credencial no encontrada")
        restored = await self._repo.restore(row)
        return self._to_response(restored)

    @staticmethod
    def _to_response(
        row: OrganizationGatewayCredentialModel,
    ) -> OrganizationGatewayCredentialResponse:
        return OrganizationGatewayCredentialResponse(
            id=row.id,
            organization_id=row.organization_id,
            provider=row.provider,
            public_config=row.public_config or {},
            secret_keys=sorted((row.secrets or {}).keys()),
            lookup_key=row.lookup_key,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
