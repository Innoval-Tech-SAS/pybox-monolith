import uuid

from receivables.payment_gateways.enums.payment_gateway_enums import ReceivablesGatewayProvider
from receivables.payment_gateways.gateways.base import ReceivablesPaymentGateway
from receivables.payment_gateways.gateways.wompi.wompi_gateway import WompiGateway
from receivables.payment_gateways.services.payment_gateway_credential_service import (
    OrganizationGatewayCredentialService,
)


class ReceivablesGatewayResolver:
    """A diferencia de `billing.gateways.PaymentGatewayResolver` (resuelve por pais,
    cuentas propias de PYBOX), aqui cada organizacion tiene sus propias credenciales:
    no hay singleton por proveedor, se arma un adaptador nuevo por llamada con las
    credenciales YA descifradas de esa organizacion."""

    def __init__(self, credential_service: OrganizationGatewayCredentialService) -> None:
        self._credential_service = credential_service

    async def get_for_organization(
        self, organization_id: uuid.UUID, provider: ReceivablesGatewayProvider
    ) -> ReceivablesPaymentGateway | None:
        credentials = await self._credential_service.get_decrypted(organization_id, provider)
        if credentials is None:
            return None
        if provider == ReceivablesGatewayProvider.WOMPI:
            return WompiGateway(credentials)
        # BOLD/PAYU/EPAYCO: listados en el enum, todavia sin adaptador implementado.
        return None
