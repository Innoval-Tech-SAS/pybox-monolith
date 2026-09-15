from decimal import Decimal

from core.tools.config_tools import get_or_throw
from billing.bold.utils.bold_client import generate_integrity_hash
from billing.gateways.base import ProviderPaymentLink
from billing.invoices.enums.invoice_enums import PaymentProvider


def _to_bold_tax(tax_type: str, tax_rate: Decimal) -> str | None:
    """
    Traduce nuestro tipo/tasa de impuesto al valor que espera data-tax del
    boton de pagos Bold (ej. 'vat-19'). Bold solo documenta IVA (vat-N) e
    impuesto al consumo (iac-N); otros tipos se omiten (sin data-tax).
    """
    if tax_rate <= 0 or tax_type != "IVA":
        return None
    return f"vat-{int(tax_rate * 100)}"


class BoldGateway:
    """
    El boton de pagos de Bold es un widget de frontend: no se hacen llamadas
    HTTP al servidor de Bold desde el backend. Solo se genera el hash de
    integridad que el frontend incluye en data-integrity-signature.
    """

    name = PaymentProvider.BOLD.value

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
        integrity_signature = generate_integrity_hash(reference, amount, currency)
        return ProviderPaymentLink(
            reference=reference,
            payment_url=None,
            provider_payload={
                "apiKey": get_or_throw("BOLD_API_KEY"),
                "integritySignature": integrity_signature,
                "redirectionUrl": get_or_throw("BOLD_REDIRECTION_URL"),
                "boldTax": _to_bold_tax(tax_type, tax_rate),
            },
        )
