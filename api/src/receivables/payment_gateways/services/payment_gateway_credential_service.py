"""Resuelve y descifra la credencial de pasarela de cobro de una organización."""

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from core.security.services.credential_decryption import decrypt_credential_values
from receivables.payment_gateways.enums.payment_gateway_enums import (
    ReceivablesGatewayProvider,
)
from receivables.payment_gateways.models.payment_gateway_credential_model import (
    OrganizationGatewayCredentialModel,
)
from receivables.payment_gateways.repository.payment_gateway_credential_repository import (  # pylint: disable=line-too-long
    OrganizationGatewayCredentialRepository,
)


@dataclass(frozen=True)
class DecryptedGatewayCredential:
    """Credencial lista para usar: `values` unifica `public_config` (en claro) con los
    `secrets` YA descifrados. Solo se materializa al momento de armar un cobro."""

    organization_id: uuid.UUID
    provider: ReceivablesGatewayProvider
    values: dict[str, str]
    lookup_key: str | None

    def get(self, key: str, default: str | None = None) -> str | None:
        return self.values.get(key, default)


class OrganizationGatewayCredentialService:
    """Lectura/descifrado para uso de los adaptadores de pasarela (ver
    `billing/gateways/base.py` y skill `wompi-gateway`) — no CRUD. El CRUD
    administrado por la propia organización vive en
    `OrganizationGatewayCredentialManagementService`."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = OrganizationGatewayCredentialRepository(session)

    async def get_decrypted(
        self, organization_id: uuid.UUID, provider: ReceivablesGatewayProvider
    ) -> DecryptedGatewayCredential | None:
        row = await self._repo.get_by_organization_and_provider(
            organization_id, provider
        )
        return self._to_decrypted(row)

    async def get_active_decrypted(
        self, organization_id: uuid.UUID
    ) -> DecryptedGatewayCredential | None:
        """La credencial activa de la organización, sin importar cuál pasarela sea —
        para el checkout de autoservicio, que debe funcionar igual sin saber de
        antemano si la organización eligió Wompi o Bold (ver
        `ReceivablesGatewayResolver.get_active_for_organization`)."""
        row = await self._repo.get_active_by_organization(organization_id)
        return self._to_decrypted(row)

    async def resolve_by_lookup_key(
        self, provider: ReceivablesGatewayProvider, lookup_key: str
    ) -> DecryptedGatewayCredential | None:
        row = await self._repo.get_by_lookup_key(provider, lookup_key)
        return self._to_decrypted(row)

    @staticmethod
    def _to_decrypted(
        row: OrganizationGatewayCredentialModel | None,
    ) -> DecryptedGatewayCredential | None:
        if row is None or not row.is_active:
            return None
        values = decrypt_credential_values(row.secrets, row.public_config)
        return DecryptedGatewayCredential(
            row.organization_id, row.provider, values, row.lookup_key
        )
