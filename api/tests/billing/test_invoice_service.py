"""InvoiceService probado como unidad: repos/gateway_resolver/organization_repo mockeados
con AsyncMock/MagicMock (no hay pytest-mock instalado), sin tocar DB ni HTTP real. El
cliente de Mercado Pago (`MercadoPagoClient`, singleton) se reemplaza por un AsyncMock
directo en la instancia de servicio -- es la unica forma de aislarlo sin pegarle a la red.

Cubre el area de mayor riesgo del proyecto (dinero real): duplicados de webhook,
montos que no cuadran, condiciones de carrera entre intentos, y el flujo de cobro manual
de Mercado Pago (Orders API) con sus casos de reintento/rechazo."""

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from fastapi import HTTPException

from billing.gateways.base import ProviderPaymentLink
from billing.invoices.constants.billing_constants import ATTEMPT_TTL
from billing.invoices.enums.invoice_enums import InvoiceStatus, PaymentAttemptStatus, PaymentProvider
from billing.invoices.services.invoice_service import InvoiceService

RESOLVE_CREDENTIALS_PATH = "billing.invoices.services.invoice_service.resolve_credentials_for_country"


def make_invoice(**overrides) -> MagicMock:
    defaults = dict(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        status=InvoiceStatus.ISSUED,
        total_amount=Decimal("15000.00"),
        billing_currency="COP",
        period_year=2026,
        period_month=8,
        tax_type="IVA",
        tax_rate=Decimal("0.19"),
        paid_at=None,
        attempts=[],
    )
    defaults.update(overrides)
    invoice = MagicMock(name="InvoiceModel")
    for key, value in defaults.items():
        setattr(invoice, key, value)
    return invoice


def make_attempt(**overrides) -> MagicMock:
    defaults = dict(
        id=uuid.uuid4(),
        invoice_id=uuid.uuid4(),
        attempt_number=1,
        provider=PaymentProvider.MERCADO_PAGO,
        provider_reference="REF-1",
        provider_link_id="ORD-1",
        status=PaymentAttemptStatus.ACTIVE,
        expected_amount=15000,
        provider_payload={},
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    attempt = MagicMock(name="InvoicePaymentAttemptModel")
    for key, value in defaults.items():
        setattr(attempt, key, value)
    return attempt


def make_service():
    session = MagicMock()
    invoice_repo = AsyncMock()
    attempt_repo = AsyncMock()
    contact_repo = AsyncMock()
    organization_repo = AsyncMock()
    gateway_resolver = AsyncMock()
    service = InvoiceService(session, invoice_repo, attempt_repo, contact_repo, organization_repo, gateway_resolver)
    service._mp_client = AsyncMock()
    return service, invoice_repo, attempt_repo, organization_repo, gateway_resolver


def make_gateway(name: str = "BOLD") -> MagicMock:
    gateway = MagicMock()
    gateway.name = name
    gateway.create_payment_link = AsyncMock(
        return_value=ProviderPaymentLink(
            reference="INV-NEW", payment_url="https://pay.example/new", provider_link_id="LINK-NEW",
            provider_payload={"foo": "bar"},
        )
    )
    return gateway


def make_http_status_error() -> httpx.HTTPStatusError:
    request = httpx.Request("POST", "https://api.mercadopago.com/v1/orders/ORD-1/process")
    response = httpx.Response(402, request=request, json={"message": "rejected"})
    return httpx.HTTPStatusError("rejected", request=request, response=response)


# ---------------------------------------------------------------------------
# mark_attempt_paid / _mark_attempt_paid
# ---------------------------------------------------------------------------
class TestMarkAttemptPaid:
    async def test_duplicate_webhook_does_not_reupdate_already_paid_attempt(self):
        service, invoice_repo, attempt_repo, _org_repo, _gw = make_service()
        attempt = make_attempt(status=PaymentAttemptStatus.ACTIVE, expected_amount=15000)
        invoice = make_invoice(status=InvoiceStatus.PAYMENT_PENDING)
        attempt_repo.get_by_provider_reference = AsyncMock(return_value=attempt)
        invoice_repo.get_by_id = AsyncMock(return_value=invoice)

        await service.mark_attempt_paid("BOLD", "REF-1", Decimal("15000.00"), {"first": True})

        assert attempt.status == PaymentAttemptStatus.PAID
        assert invoice.status == InvoiceStatus.PAID
        first_paid_at = invoice.paid_at
        assert first_paid_at is not None
        assert attempt_repo.update.await_count == 1
        assert invoice_repo.update.await_count == 1

        # Reentrega del mismo webhook (reintento tipico del proveedor): el attempt ya
        # esta PAID en memoria (mismo mock, como si fuera la misma fila re-leida con lock).
        await service.mark_attempt_paid("BOLD", "REF-1", Decimal("15000.00"), {"second": True})

        assert invoice.paid_at == first_paid_at
        assert attempt.provider_payload == {"first": True}  # no se piso con el segundo payload
        assert attempt_repo.update.await_count == 1  # no volvio a actualizar
        assert invoice_repo.update.await_count == 1

    async def test_reported_amount_mismatch_does_not_mark_paid(self):
        service, invoice_repo, attempt_repo, _org_repo, _gw = make_service()
        attempt = make_attempt(status=PaymentAttemptStatus.ACTIVE, expected_amount=15000)
        attempt_repo.get_by_provider_reference = AsyncMock(return_value=attempt)

        await service.mark_attempt_paid("BOLD", "REF-1", Decimal("100.00"), {})

        assert attempt.status == PaymentAttemptStatus.ACTIVE
        attempt_repo.update.assert_not_awaited()
        invoice_repo.get_by_id.assert_not_awaited()

    async def test_corrupt_reported_amount_is_rejected_not_marked_paid(self):
        service, invoice_repo, attempt_repo, _org_repo, _gw = make_service()
        attempt = make_attempt(status=PaymentAttemptStatus.ACTIVE, expected_amount=15000)
        attempt_repo.get_by_provider_reference = AsyncMock(return_value=attempt)

        # Decimal("NaN") es un valor "numerico" invalido para redondear (quantize revienta
        # con InvalidOperation, subclase de ArithmeticError) -- no debe colarse como pago
        # valido por default.
        await service.mark_attempt_paid("BOLD", "REF-1", Decimal("NaN"), {})

        assert attempt.status == PaymentAttemptStatus.ACTIVE
        attempt_repo.update.assert_not_awaited()
        invoice_repo.get_by_id.assert_not_awaited()

    async def test_no_attempt_for_reference_is_noop(self):
        service, invoice_repo, attempt_repo, _org_repo, _gw = make_service()
        attempt_repo.get_by_provider_reference = AsyncMock(return_value=None)

        await service.mark_attempt_paid("BOLD", "REF-DESCONOCIDA", Decimal("100.00"), {})

        invoice_repo.get_by_id.assert_not_awaited()

    async def test_late_duplicate_attempt_for_same_invoice_does_not_overwrite_paid_at(self):
        """Dos intentos distintos de la MISMA factura, ambos confirmados pagos (caso real:
        el usuario reintenta y ambos links terminan cobrando). El primero ya dejo la
        factura en PAID con paid_at=T1; el segundo intento (que llega "tarde") debe
        marcarse PAID el mismo (es un hecho real), pero no debe tocar paid_at de la
        factura, que ya quedo fijado por el primero."""
        service, invoice_repo, attempt_repo, _org_repo, _gw = make_service()
        invoice_id = uuid.uuid4()
        t1 = datetime(2026, 8, 1, tzinfo=timezone.utc)
        invoice = make_invoice(status=InvoiceStatus.PAID, paid_at=t1)
        attempt_b = make_attempt(
            invoice_id=invoice_id, status=PaymentAttemptStatus.ACTIVE, expected_amount=15000,
            provider_reference="REF-B",
        )
        attempt_repo.get_by_provider_reference = AsyncMock(return_value=attempt_b)
        invoice_repo.get_by_id = AsyncMock(return_value=invoice)

        await service.mark_attempt_paid("MERCADO_PAGO", "REF-B", Decimal("15000.00"), {})

        assert attempt_b.status == PaymentAttemptStatus.PAID  # el intento en si si se marca
        assert invoice.status == InvoiceStatus.PAID
        assert invoice.paid_at == t1  # pero paid_at no se piso
        invoice_repo.update.assert_not_awaited()  # la factura ya estaba PAID, no se re-escribe


# ---------------------------------------------------------------------------
# charge_mercadopago_attempt
# ---------------------------------------------------------------------------
class TestChargeMercadopagoAttempt:
    async def test_attempt_not_found_returns_404(self):
        service, invoice_repo, _attempt_repo, _org_repo, _gw = make_service()
        invoice = make_invoice(attempts=[])
        invoice_repo.get_by_id_and_organization_id = AsyncMock(return_value=invoice)

        with pytest.raises(HTTPException) as exc_info:
            await service.charge_mercadopago_attempt(
                invoice.id, invoice.organization_id, uuid.uuid4(), "tok", "master", "credit_card", 1
            )
        assert getattr(exc_info.value, "status_code", None) == 404
        service._mp_client.get_order.assert_not_awaited()

    async def test_attempt_from_other_provider_returns_404(self):
        service, invoice_repo, _attempt_repo, _org_repo, _gw = make_service()
        attempt = make_attempt(provider=PaymentProvider.BOLD, provider_link_id=None)
        invoice = make_invoice(attempts=[attempt])
        invoice_repo.get_by_id_and_organization_id = AsyncMock(return_value=invoice)

        with pytest.raises(HTTPException) as exc_info:
            await service.charge_mercadopago_attempt(
                invoice.id, invoice.organization_id, attempt.id, "tok", "master", "credit_card", 1
            )
        assert getattr(exc_info.value, "status_code", None) == 404
        service._mp_client.get_order.assert_not_awaited()

    async def test_attempt_without_provider_link_id_returns_404(self):
        service, invoice_repo, _attempt_repo, _org_repo, _gw = make_service()
        attempt = make_attempt(provider=PaymentProvider.MERCADO_PAGO, provider_link_id=None)
        invoice = make_invoice(attempts=[attempt])
        invoice_repo.get_by_id_and_organization_id = AsyncMock(return_value=invoice)

        with pytest.raises(HTTPException) as exc_info:
            await service.charge_mercadopago_attempt(
                invoice.id, invoice.organization_id, attempt.id, "tok", "master", "credit_card", 1
            )
        assert getattr(exc_info.value, "status_code", None) == 404
        service._mp_client.get_order.assert_not_awaited()

    async def test_already_paid_attempt_returns_400_without_calling_mp(self):
        service, invoice_repo, _attempt_repo, _org_repo, _gw = make_service()
        attempt = make_attempt(status=PaymentAttemptStatus.PAID)
        invoice = make_invoice(attempts=[attempt])
        invoice_repo.get_by_id_and_organization_id = AsyncMock(return_value=invoice)

        with pytest.raises(HTTPException) as exc_info:
            await service.charge_mercadopago_attempt(
                invoice.id, invoice.organization_id, attempt.id, "tok", "master", "credit_card", 1
            )
        assert getattr(exc_info.value, "status_code", None) == 400
        assert service._mp_client.get_order.call_count == 0

    async def test_order_no_longer_created_only_syncs_no_charge(self, monkeypatch):
        service, invoice_repo, attempt_repo, organization_repo, _gw = make_service()
        attempt = make_attempt(status=PaymentAttemptStatus.ACTIVE, expected_amount=150)
        invoice = make_invoice(attempts=[attempt])
        invoice_repo.get_by_id_and_organization_id = AsyncMock(return_value=invoice)
        invoice_repo.get_by_id = AsyncMock(return_value=invoice)
        organization_repo.get_by_id = AsyncMock(return_value=MagicMock(country="MX"))
        monkeypatch.setattr(RESOLVE_CREDENTIALS_PATH, AsyncMock(return_value=MagicMock(access_token="TOKEN")))

        # Otro intento/webhook ya proceso esta Order antes de que llegara este request.
        service._mp_client.get_order = AsyncMock(
            return_value={"status": "processed", "transactions": {"payments": [{"amount": "150.00"}]}}
        )

        await service.charge_mercadopago_attempt(
            invoice.id, invoice.organization_id, attempt.id, "tok", "master", "credit_card", 1
        )

        service._mp_client.add_transaction.assert_not_awaited()
        service._mp_client.process_order.assert_not_awaited()
        assert attempt.status == PaymentAttemptStatus.PAID  # sincronizado igual, solo que sin cobrar de nuevo

    async def test_existing_transaction_skips_add_transaction_goes_to_process(self, monkeypatch):
        service, invoice_repo, attempt_repo, organization_repo, _gw = make_service()
        attempt = make_attempt(status=PaymentAttemptStatus.ACTIVE, expected_amount=150)
        invoice = make_invoice(attempts=[attempt])
        invoice_repo.get_by_id_and_organization_id = AsyncMock(return_value=invoice)
        invoice_repo.get_by_id = AsyncMock(return_value=invoice)
        organization_repo.get_by_id = AsyncMock(return_value=MagicMock(country="MX"))
        monkeypatch.setattr(RESOLVE_CREDENTIALS_PATH, AsyncMock(return_value=MagicMock(access_token="TOKEN")))

        # Un intento anterior ya agrego la transaccion (se cayo antes de procesar).
        order_created_with_transaction = {
            "status": "created", "transactions": {"payments": [{"amount": "150.00"}]},
        }
        service._mp_client.get_order = AsyncMock(return_value=order_created_with_transaction)
        service._mp_client.process_order = AsyncMock(
            return_value={"status": "processed", "transactions": {"payments": [{"amount": "150.00"}]}}
        )

        await service.charge_mercadopago_attempt(
            invoice.id, invoice.organization_id, attempt.id, "tok", "master", "credit_card", 1
        )

        service._mp_client.add_transaction.assert_not_awaited()  # evita el 409 de reintentar la transaccion
        service._mp_client.process_order.assert_awaited_once()
        assert attempt.status == PaymentAttemptStatus.PAID

    async def test_process_order_error_reraised_when_order_still_created(self, monkeypatch):
        service, invoice_repo, attempt_repo, organization_repo, _gw = make_service()
        attempt = make_attempt(status=PaymentAttemptStatus.ACTIVE, expected_amount=150)
        invoice = make_invoice(attempts=[attempt])
        invoice_repo.get_by_id_and_organization_id = AsyncMock(return_value=invoice)
        invoice_repo.get_by_id = AsyncMock(return_value=invoice)
        organization_repo.get_by_id = AsyncMock(return_value=MagicMock(country="MX"))
        monkeypatch.setattr(RESOLVE_CREDENTIALS_PATH, AsyncMock(return_value=MagicMock(access_token="TOKEN")))

        order_created_no_transaction = {"status": "created", "transactions": {"payments": []}}
        # Primera lectura (antes de cobrar) y relectura tras el error: sigue "created" ->
        # fue un fallo real de la request (ej. timeout, error de red), no un rechazo.
        service._mp_client.get_order = AsyncMock(
            side_effect=[order_created_no_transaction, order_created_no_transaction]
        )
        service._mp_client.process_order = AsyncMock(side_effect=make_http_status_error())

        with pytest.raises(httpx.HTTPStatusError):
            await service.charge_mercadopago_attempt(
                invoice.id, invoice.organization_id, attempt.id, "tok", "master", "credit_card", 1
            )
        assert attempt.status == PaymentAttemptStatus.ACTIVE  # no se toco: el error no es un resultado valido

    async def test_process_order_error_maps_to_rejected_when_order_no_longer_created(self, monkeypatch):
        service, invoice_repo, attempt_repo, organization_repo, _gw = make_service()
        attempt = make_attempt(status=PaymentAttemptStatus.ACTIVE, expected_amount=150)
        invoice = make_invoice(attempts=[attempt])
        invoice_repo.get_by_id_and_organization_id = AsyncMock(return_value=invoice)
        invoice_repo.get_by_id = AsyncMock(return_value=invoice)
        organization_repo.get_by_id = AsyncMock(return_value=MagicMock(country="MX"))
        monkeypatch.setattr(RESOLVE_CREDENTIALS_PATH, AsyncMock(return_value=MagicMock(access_token="TOKEN")))

        order_created_no_transaction = {"status": "created", "transactions": {"payments": []}}
        order_failed = {"status": "failed", "transactions": {"payments": []}}
        # MP respondio error HTTP, pero al releer la Order ya salio de "created": fue un
        # rechazo legitimo (ej. fondos insuficientes), no un fallo de la request.
        service._mp_client.get_order = AsyncMock(side_effect=[order_created_no_transaction, order_failed])
        service._mp_client.process_order = AsyncMock(side_effect=make_http_status_error())

        result = await service.charge_mercadopago_attempt(
            invoice.id, invoice.organization_id, attempt.id, "tok", "master", "credit_card", 1
        )

        assert result is invoice
        assert attempt.status == PaymentAttemptStatus.REJECTED

    async def test_missing_credentials_for_country_returns_400_before_mp(self, monkeypatch):
        service, invoice_repo, attempt_repo, organization_repo, _gw = make_service()
        attempt = make_attempt(status=PaymentAttemptStatus.ACTIVE)
        invoice = make_invoice(attempts=[attempt])
        invoice_repo.get_by_id_and_organization_id = AsyncMock(return_value=invoice)
        organization_repo.get_by_id = AsyncMock(return_value=MagicMock(country="MX"))
        monkeypatch.setattr(RESOLVE_CREDENTIALS_PATH, AsyncMock(return_value=None))

        with pytest.raises(HTTPException) as exc_info:
            await service.charge_mercadopago_attempt(
                invoice.id, invoice.organization_id, attempt.id, "tok", "master", "credit_card", 1
            )
        assert getattr(exc_info.value, "status_code", None) == 400
        service._mp_client.get_order.assert_not_awaited()


# ---------------------------------------------------------------------------
# create_or_reuse_payment_link
# ---------------------------------------------------------------------------
class TestCreateOrReusePaymentLink:
    @pytest.mark.parametrize("status", [InvoiceStatus.PAID, InvoiceStatus.CANCELLED])
    async def test_terminal_invoice_status_returns_400(self, status):
        service, invoice_repo, _attempt_repo, organization_repo, gateway_resolver = make_service()
        invoice = make_invoice(status=status)
        invoice_repo.get_by_id_and_organization_id = AsyncMock(return_value=invoice)

        with pytest.raises(HTTPException) as exc_info:
            await service.create_or_reuse_payment_link(invoice.id, invoice.organization_id, "payer@example.com")
        assert getattr(exc_info.value, "status_code", None) == 400
        gateway_resolver.get_for_country.assert_not_awaited()

    async def test_reuses_active_attempt_within_ttl(self):
        service, invoice_repo, attempt_repo, organization_repo, gateway_resolver = make_service()
        invoice = make_invoice(status=InvoiceStatus.ISSUED)
        invoice_repo.get_by_id_and_organization_id = AsyncMock(return_value=invoice)
        organization_repo.get_by_id = AsyncMock(return_value=MagicMock(country=None))
        gateway = make_gateway("BOLD")
        gateway_resolver.get_for_country = AsyncMock(return_value=gateway)

        latest_attempt = make_attempt(
            status=PaymentAttemptStatus.ACTIVE, provider=PaymentProvider.BOLD, provider_reference="REF-OLD",
            created_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        )
        attempt_repo.get_latest_by_invoice_id = AsyncMock(return_value=latest_attempt)

        result = await service.create_or_reuse_payment_link(invoice.id, invoice.organization_id, "payer@example.com")

        assert result.reused is True
        assert result.order_id == "REF-OLD"
        gateway.create_payment_link.assert_not_awaited()
        attempt_repo.add.assert_not_awaited()

    async def test_expired_active_attempt_creates_new(self):
        service, invoice_repo, attempt_repo, organization_repo, gateway_resolver = make_service()
        invoice = make_invoice(status=InvoiceStatus.ISSUED)
        invoice_repo.get_by_id_and_organization_id = AsyncMock(return_value=invoice)
        organization_repo.get_by_id = AsyncMock(return_value=MagicMock(country=None))
        gateway = make_gateway("BOLD")
        gateway_resolver.get_for_country = AsyncMock(return_value=gateway)

        latest_attempt = make_attempt(
            status=PaymentAttemptStatus.ACTIVE, provider=PaymentProvider.BOLD, provider_reference="REF-OLD",
            created_at=datetime.now(timezone.utc) - ATTEMPT_TTL - timedelta(minutes=1),
        )
        attempt_repo.get_latest_by_invoice_id = AsyncMock(return_value=latest_attempt)
        attempt_repo.add = AsyncMock(return_value=make_attempt(status=PaymentAttemptStatus.ACTIVE))

        result = await service.create_or_reuse_payment_link(invoice.id, invoice.organization_id, "payer@example.com")

        assert result.reused is False
        gateway.create_payment_link.assert_awaited_once()
        attempt_repo.add.assert_awaited_once()

    async def test_active_attempt_from_other_provider_is_not_reused(self):
        service, invoice_repo, attempt_repo, organization_repo, gateway_resolver = make_service()
        invoice = make_invoice(status=InvoiceStatus.ISSUED)
        invoice_repo.get_by_id_and_organization_id = AsyncMock(return_value=invoice)
        organization_repo.get_by_id = AsyncMock(return_value=MagicMock(country=None))
        gateway = make_gateway("BOLD")
        gateway_resolver.get_for_country = AsyncMock(return_value=gateway)

        latest_attempt = make_attempt(
            status=PaymentAttemptStatus.ACTIVE, provider=PaymentProvider.MERCADO_PAGO,
            provider_reference="REF-OLD", created_at=datetime.now(timezone.utc),
        )
        attempt_repo.get_latest_by_invoice_id = AsyncMock(return_value=latest_attempt)
        attempt_repo.add = AsyncMock(return_value=make_attempt(status=PaymentAttemptStatus.ACTIVE))

        result = await service.create_or_reuse_payment_link(invoice.id, invoice.organization_id, "payer@example.com")

        assert result.reused is False
        gateway.create_payment_link.assert_awaited_once()

    @pytest.mark.parametrize(
        "status",
        [
            PaymentAttemptStatus.PAID,
            PaymentAttemptStatus.EXPIRED,
            PaymentAttemptStatus.REJECTED,
            PaymentAttemptStatus.CANCELLED,
        ],
    )
    async def test_terminal_attempt_status_always_creates_new(self, status):
        service, invoice_repo, attempt_repo, organization_repo, gateway_resolver = make_service()
        invoice = make_invoice(status=InvoiceStatus.ISSUED)
        invoice_repo.get_by_id_and_organization_id = AsyncMock(return_value=invoice)
        organization_repo.get_by_id = AsyncMock(return_value=MagicMock(country=None))
        gateway = make_gateway("BOLD")
        gateway_resolver.get_for_country = AsyncMock(return_value=gateway)

        latest_attempt = make_attempt(
            status=status, provider=PaymentProvider.BOLD, provider_reference="REF-OLD",
            created_at=datetime.now(timezone.utc),
        )
        attempt_repo.get_latest_by_invoice_id = AsyncMock(return_value=latest_attempt)
        attempt_repo.add = AsyncMock(return_value=make_attempt(status=PaymentAttemptStatus.ACTIVE))

        result = await service.create_or_reuse_payment_link(invoice.id, invoice.organization_id, "payer@example.com")

        assert result.reused is False
        gateway.create_payment_link.assert_awaited_once()
