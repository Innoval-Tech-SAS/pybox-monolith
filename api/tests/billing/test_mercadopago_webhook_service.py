"""MercadoPagoWebhookService probado como unidad: invoice_service, credenciales y
verificador de firma mockeados con AsyncMock/MagicMock/patch (sin pytest-mock). El
cliente de Mercado Pago (singleton) se reemplaza por un AsyncMock directo en la
instancia. Foco: que un webhook falso o de una cuenta desconocida no pueda tocar
estado de facturacion antes de pasar los gates de identidad/firma/topico."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from billing.mercadopago.services.mercadopago_webhook_service import (
    MercadoPagoWebhookService,
)

MODULE = "billing.mercadopago.services.mercadopago_webhook_service"


def make_service():
    invoice_service = AsyncMock()
    session = MagicMock()
    service = MercadoPagoWebhookService(invoice_service, session)
    service._client = AsyncMock()
    return service, invoice_service


def make_credentials(webhook_secret="secret", access_token="token", country="MX"):
    return MagicMock(
        webhook_secret=webhook_secret, access_token=access_token, country=country
    )


class TestProcessWebhook:
    async def test_unknown_application_id_returns_401_without_calling_get_order(
        self, monkeypatch
    ):
        service, invoice_service = make_service()
        monkeypatch.setattr(
            f"{MODULE}.resolve_credentials_for_application_id",
            AsyncMock(return_value=None),
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.process_webhook(
                {"application_id": "UNKNOWN", "type": "order"}, "ORD1", "sig", "req1"
            )
        assert exc_info.value.status_code == 401
        service._client.get_order.assert_not_awaited()
        invoice_service.sync_attempt_status_by_link_id.assert_not_awaited()

    async def test_production_with_invalid_signature_returns_401_before_get_order(
        self, monkeypatch
    ):
        service, invoice_service = make_service()
        monkeypatch.setattr(
            f"{MODULE}.resolve_credentials_for_application_id",
            AsyncMock(return_value=make_credentials()),
        )
        monkeypatch.setattr(
            f"{MODULE}.verify_mercadopago_signature", MagicMock(return_value=False)
        )
        monkeypatch.setattr(
            f"{MODULE}.get_or_throw", MagicMock(return_value="production")
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.process_webhook(
                {"application_id": "APP1", "type": "order"}, "ORD1", "bad-sig", "req1"
            )
        assert exc_info.value.status_code == 401
        service._client.get_order.assert_not_awaited()

    async def test_non_production_with_invalid_signature_continues_and_calls_get_order(
        self, monkeypatch
    ):
        service, invoice_service = make_service()
        monkeypatch.setattr(
            f"{MODULE}.resolve_credentials_for_application_id",
            AsyncMock(return_value=make_credentials()),
        )
        monkeypatch.setattr(
            f"{MODULE}.verify_mercadopago_signature", MagicMock(return_value=False)
        )
        monkeypatch.setattr(
            f"{MODULE}.get_or_throw", MagicMock(return_value="development")
        )
        service._client.get_order = AsyncMock(
            return_value={
                "id": "ORD1",
                "status": "processed",
                "transactions": {"payments": [{"amount": "10.00"}]},
            }
        )

        await service.process_webhook(
            {"application_id": "APP1", "type": "order"}, "ORD1", "bad-sig", "req1"
        )

        service._client.get_order.assert_awaited_once()
        invoice_service.sync_attempt_status_by_link_id.assert_awaited_once()

    async def test_non_order_type_returns_without_calling_get_order(self, monkeypatch):
        service, invoice_service = make_service()
        monkeypatch.setattr(
            f"{MODULE}.resolve_credentials_for_application_id",
            AsyncMock(return_value=make_credentials()),
        )
        monkeypatch.setattr(
            f"{MODULE}.verify_mercadopago_signature", MagicMock(return_value=True)
        )
        monkeypatch.setattr(
            f"{MODULE}.get_or_throw", MagicMock(return_value="production")
        )

        await service.process_webhook(
            {"application_id": "APP1", "type": "payment"}, "PAY1", "sig", "req1"
        )

        service._client.get_order.assert_not_awaited()
        invoice_service.sync_attempt_status_by_link_id.assert_not_awaited()

    async def test_unmapped_order_status_does_not_touch_attempt_or_invoice(
        self, monkeypatch
    ):
        service, invoice_service = make_service()
        monkeypatch.setattr(
            f"{MODULE}.resolve_credentials_for_application_id",
            AsyncMock(return_value=make_credentials()),
        )
        monkeypatch.setattr(
            f"{MODULE}.verify_mercadopago_signature", MagicMock(return_value=True)
        )
        monkeypatch.setattr(
            f"{MODULE}.get_or_throw", MagicMock(return_value="production")
        )
        # "refunded" no tiene transicion de PaymentAttemptStatus (ver mercadopago_status_mapper.py):
        # la factura ya estaba PAID antes del reembolso, eso se maneja aparte.
        service._client.get_order = AsyncMock(
            return_value={
                "id": "ORD1",
                "status": "refunded",
                "transactions": {"payments": []},
            }
        )

        await service.process_webhook(
            {"application_id": "APP1", "type": "order"}, "ORD1", "sig", "req1"
        )

        service._client.get_order.assert_awaited_once()
        invoice_service.sync_attempt_status_by_link_id.assert_not_awaited()
