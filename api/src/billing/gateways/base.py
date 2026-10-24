"""Protocol común de las pasarelas de pago de suscripción/facturación (Bold, MP)."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Protocol


@dataclass
class ProviderPaymentLink:
    reference: str
    payment_url: str | None
    provider_payload: dict[str, Any] = field(default_factory=dict)
    provider_link_id: str | None = None


class PaymentGateway(Protocol):
    name: str

    async def create_payment_link(
        self,
        reference: str,
        amount: int,
        currency: str,
        description: str,
        tax_type: str,
        tax_rate: Decimal,
        payer_email: str,
    ) -> ProviderPaymentLink: ...
