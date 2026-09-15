"""Bold: verificador de firma (funcion pura, HMAC) y el servicio de webhook que lo usa
como gate de entrada. El servicio se prueba con `verify_bold_signature` parcheado via
`unittest.mock.patch` (no hay pytest-mock) para aislar del HMAC real; el verificador se
prueba directo, con `BOLD_SECRET_KEY` fijada por `monkeypatch.setenv`."""

import base64
import hashlib
import hmac
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from billing.bold.enums.bold_enums import BoldLinkStatus
from billing.bold.services.bold_webhook_service import BoldWebhookService
from billing.bold.utils.bold_client import generate_integrity_hash
from billing.bold.utils.bold_status_mapper import bold_link_status_to_attempt_status
from billing.bold.utils.bold_webhook_verifier import verify_bold_signature
from billing.invoices.enums.invoice_enums import PaymentAttemptStatus


def _sign(raw_body: bytes, secret_key: str) -> str:
    encoded = base64.b64encode(raw_body)
    return hmac.new(secret_key.encode("utf-8"), encoded, hashlib.sha256).hexdigest()


class TestVerifyBoldSignature:
    def test_missing_signature_returns_false(self, monkeypatch):
        monkeypatch.setenv("BOLD_SECRET_KEY", "top-secret")
        assert verify_bold_signature(b'{"type": "SALE_APPROVED"}', None) is False

    def test_invalid_signature_returns_false(self, monkeypatch):
        monkeypatch.setenv("BOLD_SECRET_KEY", "top-secret")
        assert verify_bold_signature(b'{"type": "SALE_APPROVED"}', "not-the-real-signature") is False

    def test_empty_body_with_wrong_signature_returns_false(self, monkeypatch):
        monkeypatch.setenv("BOLD_SECRET_KEY", "top-secret")
        assert verify_bold_signature(b"", "not-the-real-signature") is False

    def test_valid_signature_returns_true(self, monkeypatch):
        monkeypatch.setenv("BOLD_SECRET_KEY", "top-secret")
        body = b'{"type": "SALE_APPROVED", "data": {"metadata": {"reference": "INV-1"}}}'
        signature = _sign(body, "top-secret")
        assert verify_bold_signature(body, signature) is True

    def test_empty_secret_key_still_validates_correct_signature(self, monkeypatch):
        # Docstring del verificador: en sandbox Bold firma con secret vacio.
        monkeypatch.setenv("BOLD_SECRET_KEY", "")
        body = b'{"type": "SALE_APPROVED"}'
        signature = _sign(body, "")
        assert verify_bold_signature(body, signature) is True


class TestBoldWebhookServiceProcessWebhook:
    def _service(self):
        invoice_service = AsyncMock()
        return BoldWebhookService(invoice_service), invoice_service

    async def test_invalid_signature_returns_401_without_processing(self):
        service, invoice_service = self._service()
        with patch("billing.bold.services.bold_webhook_service.verify_bold_signature", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await service.process_webhook(b'{"type": "SALE_APPROVED"}', "bad-sig")
        assert exc_info.value.status_code == 401
        invoice_service.mark_attempt_paid.assert_not_awaited()

    async def test_non_sale_approved_type_does_not_mark_paid(self):
        service, invoice_service = self._service()
        body = b'{"type": "SALE_REJECTED", "data": {"metadata": {"reference": "INV-1"}}}'
        with patch("billing.bold.services.bold_webhook_service.verify_bold_signature", return_value=True):
            await service.process_webhook(body, "sig")
        invoice_service.mark_attempt_paid.assert_not_awaited()

    async def test_sale_approved_without_reference_does_not_mark_paid(self):
        service, invoice_service = self._service()
        body = b'{"type": "SALE_APPROVED", "data": {"metadata": {}}}'
        with patch("billing.bold.services.bold_webhook_service.verify_bold_signature", return_value=True):
            await service.process_webhook(body, "sig")
        invoice_service.mark_attempt_paid.assert_not_awaited()

    async def test_sale_approved_missing_data_entirely_does_not_mark_paid(self):
        service, invoice_service = self._service()
        body = b'{"type": "SALE_APPROVED"}'
        with patch("billing.bold.services.bold_webhook_service.verify_bold_signature", return_value=True):
            await service.process_webhook(body, "sig")
        invoice_service.mark_attempt_paid.assert_not_awaited()

    async def test_invalid_json_body_does_not_crash_and_does_not_process(self):
        service, invoice_service = self._service()
        body = b"{not-valid-json{{{"
        with patch("billing.bold.services.bold_webhook_service.verify_bold_signature", return_value=True):
            await service.process_webhook(body, "sig")  # no debe lanzar
        invoice_service.mark_attempt_paid.assert_not_awaited()

    async def test_sale_approved_with_reference_marks_paid(self):
        service, invoice_service = self._service()
        body = b'{"type": "SALE_APPROVED", "data": {"amount": 15000, "metadata": {"reference": "INV-1-1"}}}'
        with patch("billing.bold.services.bold_webhook_service.verify_bold_signature", return_value=True):
            await service.process_webhook(body, "sig")
        invoice_service.mark_attempt_paid.assert_awaited_once()
        args = invoice_service.mark_attempt_paid.await_args.args
        assert args[0] == "BOLD"
        assert args[1] == "INV-1-1"
        assert args[2] == Decimal("15000")


class TestBoldLinkStatusToAttemptStatus:
    """Tabla completa: cada BoldLinkStatus debe mapear exactamente al
    PaymentAttemptStatus documentado -- a diferencia del mapper de Mercado Pago, este
    es un dict total (sin status "no mapeados"), asi que un KeyError aqui indicaria
    que el enum de Bold crecio sin actualizar el mapper."""

    @pytest.mark.parametrize(
        "bold_status,expected",
        [
            (BoldLinkStatus.ACTIVE, PaymentAttemptStatus.ACTIVE),
            (BoldLinkStatus.PROCESSING, PaymentAttemptStatus.PROCESSING),
            (BoldLinkStatus.PAID, PaymentAttemptStatus.PAID),
            (BoldLinkStatus.EXPIRED, PaymentAttemptStatus.EXPIRED),
            (BoldLinkStatus.REJECTED, PaymentAttemptStatus.REJECTED),
            (BoldLinkStatus.CANCELLED, PaymentAttemptStatus.CANCELLED),
        ],
    )
    def test_maps_to_expected_attempt_status(self, bold_status, expected):
        assert bold_link_status_to_attempt_status(bold_status) == expected

    def test_table_covers_every_member_of_the_enum(self):
        for status in BoldLinkStatus:
            assert bold_link_status_to_attempt_status(status) is not None


class TestGenerateIntegrityHash:
    """generate_integrity_hash es SHA256(f"{order_id}{amount_pesos}{currency}{secret}")
    -- se recalcula la formula en el test (no un hash pegado a mano) para validar que
    la implementacion siga exactamente esa formula documentada, ya que el frontend
    (Boton de pagos Bold) la recalcula tambien y cualquier divergencia rompe el cobro
    en silencio (Bold rechaza el widget sin decir por que)."""

    def test_hash_matches_documented_formula(self, monkeypatch):
        monkeypatch.setenv("BOLD_SECRET_KEY", "top-secret")
        expected = hashlib.sha256(b"INV-1150000COPtop-secret").hexdigest()

        assert generate_integrity_hash("INV-1", 150000, "COP") == expected

    def test_hash_is_deterministic_for_same_inputs(self, monkeypatch):
        monkeypatch.setenv("BOLD_SECRET_KEY", "top-secret")

        first = generate_integrity_hash("INV-2", 5000, "COP")
        second = generate_integrity_hash("INV-2", 5000, "COP")

        assert first == second

    @pytest.mark.parametrize(
        "order_id,amount,currency",
        [("INV-3", 5000, "COP"), ("INV-2", 5001, "COP"), ("INV-2", 5000, "USD")],
    )
    def test_changing_any_input_changes_the_hash(self, monkeypatch, order_id, amount, currency):
        monkeypatch.setenv("BOLD_SECRET_KEY", "top-secret")
        baseline = generate_integrity_hash("INV-2", 5000, "COP")

        assert generate_integrity_hash(order_id, amount, currency) != baseline

    def test_different_secret_key_changes_the_hash(self, monkeypatch):
        monkeypatch.setenv("BOLD_SECRET_KEY", "secret-a")
        hash_a = generate_integrity_hash("INV-1", 1000, "COP")
        monkeypatch.setenv("BOLD_SECRET_KEY", "secret-b")
        hash_b = generate_integrity_hash("INV-1", 1000, "COP")

        assert hash_a != hash_b

    def test_missing_secret_key_raises(self, monkeypatch):
        monkeypatch.delenv("BOLD_SECRET_KEY", raising=False)

        with pytest.raises(RuntimeError):
            generate_integrity_hash("INV-1", 1000, "COP")
