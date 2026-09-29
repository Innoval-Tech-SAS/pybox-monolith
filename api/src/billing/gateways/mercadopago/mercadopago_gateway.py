"""Adaptador de Mercado Pago vía Orders API en modo manual."""

from decimal import Decimal

from billing.gateways.base import ProviderPaymentLink
from billing.invoices.enums.invoice_enums import PaymentProvider
from billing.mercadopago.services.mercadopago_client import MercadoPagoClient
from billing.mercadopago.utils.mercadopago_credentials import MercadoPagoCredentials


class MercadoPagoGateway:
    """
    Integracion via Orders API (Checkout API moderno) en modo manual: el backend solo
    crea la Order y devuelve el `client_token`; la tarjeta se captura y procesa en el
    frontend con el SDK de Mercado Pago, sin pasar por este backend. El estado final
    se confirma via webhook (topico "order"), igual que con Bold.

    Las credenciales se inyectan por pais (ver mercadopago_credentials.py): esta misma
    clase sirve para cualquier pais que use Mercado Pago, solo cambia la instancia con
    la que se registra en billing/gateways/resolver.py.
    """

    name = PaymentProvider.MERCADO_PAGO.value

    def __init__(self, credentials: MercadoPagoCredentials):
        self._credentials = credentials
        self._client = MercadoPagoClient()

    async def create_payment_link(
        self,
        reference: str,
        amount: int,
        _currency: str,
        description: str,
        _tax_type: str,
        _tax_rate: Decimal,
        payer_email: str,
    ) -> ProviderPaymentLink:
        # `currency` es parte de la firma compartida con BoldGateway pero la Orders API
        # de MP no acepta moneda explicita: la infiere de la cuenta del `access_token`
        # (ver docstring de create_order_manual). Por eso cada pais requiere su propia
        # cuenta de MP en vez de forzar la moneda desde aqui.
        order = await self._client.create_order_manual(
            self._credentials.access_token, reference, amount, description, payer_email
        )
        return ProviderPaymentLink(
            reference=reference,
            payment_url=None,
            provider_link_id=order["id"],
            provider_payload={
                "publicKey": self._credentials.public_key,
                "orderId": order["id"],
                "clientToken": order.get("client_token"),
            },
        )
