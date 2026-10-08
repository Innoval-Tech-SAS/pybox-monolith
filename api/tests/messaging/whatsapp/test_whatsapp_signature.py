"""Tests de verify_whatsapp_signature (ver whatsapp_signature.py) -- HMAC-SHA256 del
body crudo del webhook contra el `app_secret` de la app de Meta, header
`X-Hub-Signature-256: sha256=<hex>`.
"""

import hashlib
import hmac
from unittest.mock import patch

from messaging.whatsapp.utils.whatsapp_signature import verify_whatsapp_signature

APP_SECRET = "un-secreto-de-app-de-meta"


def _sign(raw_body: bytes, secret: str = APP_SECRET) -> str:
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


class TestVerifyWhatsAppSignature:
    def test_valid_signature_returns_true(self):
        raw_body = b'{"entry": []}'
        signature = _sign(raw_body)

        with patch(
            "messaging.whatsapp.utils.whatsapp_signature.get_or_throw", return_value=APP_SECRET
        ):
            assert verify_whatsapp_signature(raw_body, signature) is True

    def test_tampered_body_fails_verification(self):
        raw_body = b'{"entry": []}'
        signature = _sign(raw_body)
        tampered_body = b'{"entry": ["injected"]}'

        with patch(
            "messaging.whatsapp.utils.whatsapp_signature.get_or_throw", return_value=APP_SECRET
        ):
            assert verify_whatsapp_signature(tampered_body, signature) is False

    def test_signature_signed_with_wrong_secret_fails(self):
        raw_body = b'{"entry": []}'
        signature = _sign(raw_body, secret="otro-secreto")

        with patch(
            "messaging.whatsapp.utils.whatsapp_signature.get_or_throw", return_value=APP_SECRET
        ):
            assert verify_whatsapp_signature(raw_body, signature) is False

    def test_missing_signature_header_returns_false_without_reading_secret(self):
        with patch("messaging.whatsapp.utils.whatsapp_signature.get_or_throw") as mock_get:
            assert verify_whatsapp_signature(b"body", None) is False
            mock_get.assert_not_called()

    def test_signature_without_sha256_prefix_returns_false(self):
        with patch("messaging.whatsapp.utils.whatsapp_signature.get_or_throw") as mock_get:
            assert verify_whatsapp_signature(b"body", "not-a-valid-prefix") is False
            mock_get.assert_not_called()

    def test_empty_string_signature_returns_false(self):
        assert verify_whatsapp_signature(b"body", "") is False
