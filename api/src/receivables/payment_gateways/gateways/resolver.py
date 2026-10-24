"""Resuelve qué pasarela de cobro usar según la configuración de la organización."""

import uuid

from receivables.payment_gateways.enums.payment_gateway_enums import (
    ReceivablesGatewayProvider,
)
from receivables.payment_gateways.gateways.base import ReceivablesPaymentGateway
from receivables.payment_gateways.gateways.bold.bold_gateway import BoldGateway
from receivables.payment_gateways.gateways.wompi.wompi_gateway import WompiGateway
from receivables.payment_gateways.services.payment_gateway_credential_service import (
    DecryptedGatewayCredential,
    OrganizationGatewayCredentialService,
)


class ReceivablesGatewayResolver:
    """A diferencia de `billing.gateways.PaymentGatewayResolver` (resuelve por pais,
    cuentas propias de PYBOX), aqui cada organizacion tiene sus propias credenciales:
    no hay singleton por proveedor, se arma un adaptador nuevo por llamada con las
    credenciales YA descifradas de esa organizacion."""

    def __init__(
        self, credential_service: OrganizationGatewayCredentialService
    ) -> None:
        self._credential_service = credential_service

    async def get_for_organization(
        self, organization_id: uuid.UUID, provider: ReceivablesGatewayProvider
    ) -> ReceivablesPaymentGateway | None:
        """Resuelve una pasarela EXPLÍCITA, conocida de antemano por el llamador (ej.
        el webhook de Wompi, cuya URL ya fija el proveedor). El checkout de
        autoservicio no debe usar este método: ver `get_active_for_organization`."""
        credentials = await self._credential_service.get_decrypted(
            organization_id, provider
        )
        if credentials is None:
            return None
        return self._build(credentials)

    async def get_active_for_organization(
        self, organization_id: uuid.UUID
    ) -> ReceivablesPaymentGateway | None:
        """Resuelve la pasarela activa de la organización sin que el llamador sepa de
        antemano cuál es (checkout/fuentes de pago del autoservicio -- la organización
        pudo haber elegido Wompi o Bold, nunca las dos a la vez, ver
        `OrganizationGatewayCredentialManagementService`)."""
        credentials = await self._credential_service.get_active_decrypted(
            organization_id
        )
        if credentials is None:
            return None
        return self._build(credentials)

    @staticmethod
    def _build(
        credentials: DecryptedGatewayCredential,
    ) -> ReceivablesPaymentGateway | None:
        if credentials.provider == ReceivablesGatewayProvider.WOMPI:
            return WompiGateway(credentials)
        if credentials.provider == ReceivablesGatewayProvider.BOLD:
            return BoldGateway(credentials)
        return None
