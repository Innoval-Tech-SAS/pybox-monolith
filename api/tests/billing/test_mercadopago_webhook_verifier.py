"""verify_mercadopago_signature probado en dos capas:

1. Con el SDK REAL (`mercadopago.webhook.WebhookSignatureValidator`), construyendo una
   firma HMAC valida a mano con la misma formula que usa MP -- cubre el detalle mas
   fragil del modulo: el `data_id` de la Orders API llega en MAYUSCULAS pero MP firma
   el manifest en minusculas, así que hay que pasarlo en `.lower()` o la firma nunca
   cuadra.
2. Con `WebhookSignatureValidator.validate` mockeado via `unittest.mock.patch` (sin
   pytest-mock), para el caso de excepcion sin depender del detalle interno del SDK.
"""

import hashlib
import hmac
import time
from unittest.mock import MagicMock, patch

from mercadopago.webhook import InvalidWebhookSignatureError, SignatureFailureReason

from billing.mercadopago.utils.mercadopago_webhook_verifier import (
    verify_mercadopago_signature,
)

MODULE = "billing.mercadopago.utils.mercadopago_webhook_verifier"
VALIDATOR_TARGET = f"{MODULE}.WebhookSignatureValidator.validate"


def _sign(
    data_id: str, x_request_id: str | None, secret: str, ts: str | None = None
) -> tuple[str, str]:
    """Replica `_build_manifest`/HMAC del SDK: 'id:<id>;request-id:<rid>;ts:<ts>;'."""
    ts = ts or str(int(time.time()))
    parts = []
    if data_id:
        parts.append(f"id:{data_id}")
    if x_request_id:
        parts.append(f"request-id:{x_request_id}")
    parts.append(f"ts:{ts}")
    manifest = ";".join(parts) + ";"
    signature = hmac.new(
        secret.encode("utf-8"), manifest.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return f"ts={ts},v1={signature}", ts


class TestVerifyMercadopagoSignatureRealSdk:
    def test_valid_signature_with_uppercase_data_id_returns_true(self):
        """El bug clasico: la Orders API manda `data.id` en MAYUSCULAS (ej. 'ORD01...')
        pero MP firma en minusculas -- si `verify_mercadopago_signature` no hiciera
        `.lower()`, esto fallaria siempre en produccion."""
        secret = "top-secret"
        x_signature, _ts = _sign("ord01abc123", "req-1", secret)

        assert (
            verify_mercadopago_signature("ORD01ABC123", "req-1", x_signature, secret)
            is True
        )

    def test_signature_computed_with_wrong_secret_returns_false(self):
        x_signature, _ts = _sign("ord1", "req-1", "correct-secret")

        assert (
            verify_mercadopago_signature("ORD1", "req-1", x_signature, "wrong-secret")
            is False
        )

    def test_missing_signature_header_returns_false(self):
        assert (
            verify_mercadopago_signature("ORD1", "req-1", None, "any-secret") is False
        )

    def test_malformed_signature_header_returns_false(self):
        assert (
            verify_mercadopago_signature(
                "ORD1", "req-1", "not-a-valid-header", "any-secret"
            )
            is False
        )

    def test_numeric_data_id_lowercase_is_a_noop(self):
        # Ids numericos (otros topicos, no "order") no tienen mayusculas que perder --
        # `.lower()` debe ser inofensivo.
        secret = "top-secret"
        x_signature, _ts = _sign("123456789", "req-1", secret)

        assert (
            verify_mercadopago_signature("123456789", "req-1", x_signature, secret)
            is True
        )

    def test_mismatched_request_id_invalidates_signature(self):
        secret = "top-secret"
        x_signature, _ts = _sign("ord1", "req-original", secret)

        assert (
            verify_mercadopago_signature("ORD1", "req-otro", x_signature, secret)
            is False
        )


class TestVerifyMercadopagoSignatureMockedValidator:
    def test_validator_success_returns_true(self):
        with patch(VALIDATOR_TARGET, MagicMock(return_value=None)) as validate:
            assert (
                verify_mercadopago_signature(
                    "ORD1ABC", "req-1", "ts=1,v1=abc", "secret"
                )
                is True
            )
        # El data_id se pasa en minusculas al validador del SDK.
        args, _kwargs = validate.call_args
        assert args[2] == "ord1abc"

    def test_validator_raises_invalid_signature_returns_false(self):
        error = InvalidWebhookSignatureError(
            SignatureFailureReason.SIGNATURE_MISMATCH, "req-1", "12345"
        )
        with patch(VALIDATOR_TARGET, MagicMock(side_effect=error)):
            assert (
                verify_mercadopago_signature("ORD1", "req-1", "ts=1,v1=bad", "secret")
                is False
            )
