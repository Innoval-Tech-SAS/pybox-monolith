from decimal import Decimal

from billing.gateways.base import ProviderPaymentLink


class UnsupportedGateway:
    name = "UNSUPPORTED"

    async def create_payment_link(
        self,
        reference: str,
        amount: int,
        currency: str,
        description: str,
        tax_type: str,
        tax_rate: Decimal,
        payer_email: str,
    ) -> ProviderPaymentLink:
        raise NotImplementedError("Pasarela de pago no configurada para este país")
