"""Firma de PayU -- el caso `test_request_signature_matches_official_example` usa el
ejemplo textual publicado por PayU en developers.payulatam.com (sección "Authentication
Signature"): confirma la fórmula contra la fuente oficial, no solo contra el SDK."""

import hashlib

from receivables.payment_gateways.gateways.payu.payu_signature import (
    build_payu_request_signature,
    verify_payu_confirmation_signature,
)


class TestBuildPayuRequestSignature:
    def test_matches_official_example(self):
        signature = build_payu_request_signature(
            api_key="4Vj8eK4rloUd272L48hsrarnUA",
            merchant_id="508029",
            reference_code="TestPayU",
            amount_in_cents=300,  # $3 USD, el ejemplo oficial no usa COP
            currency="USD",
        )
        assert signature == "ba9ffa71559580175585e45ce70b6c37"

    def test_amount_is_truncated_to_whole_pesos(self):
        # 65000 COP exactos (6500000 centavos) y 65000.99 (6500099 centavos) deben
        # firmar igual -- PayU Latam no firma centavos de peso (ver SignatureUtil.php).
        signature_exact = build_payu_request_signature(
            "key", "123", "REF-1", 6_500_000, "COP"
        )
        signature_with_cents = build_payu_request_signature(
            "key", "123", "REF-1", 6_500_099, "COP"
        )
        assert signature_exact == signature_with_cents


class TestVerifyPayuConfirmationSignature:
    def _fields(self, **overrides: str) -> dict[str, str]:
        base = {
            "merchant_id": "508029",
            "reference_sale": "PAG-TEST-1",
            "value": "65000.00",
            "currency": "COP",
            "state_pol": "4",
        }
        base.update(overrides)
        return base

    def test_accepts_matching_signature_with_whole_value(self):
        fields = self._fields()
        message = "4Vj8eK4rloUd272L48hsrarnUA~508029~PAG-TEST-1~65000.0~COP~4"
        fields["sign"] = hashlib.md5(message.encode("utf-8")).hexdigest()
        assert verify_payu_confirmation_signature(fields, "4Vj8eK4rloUd272L48hsrarnUA")

    def test_rejects_mismatched_signature(self):
        fields = self._fields(sign="deadbeef")
        assert not verify_payu_confirmation_signature(
            fields, "4Vj8eK4rloUd272L48hsrarnUA"
        )

    def test_rejects_when_value_is_not_numeric(self):
        fields = self._fields(value="not-a-number", sign="deadbeef")
        assert not verify_payu_confirmation_signature(
            fields, "4Vj8eK4rloUd272L48hsrarnUA"
        )

    def test_value_with_nonzero_hundredths_keeps_two_decimals(self):
        fields = self._fields(value="65000.25")
        message = "4Vj8eK4rloUd272L48hsrarnUA~508029~PAG-TEST-1~65000.25~COP~4"
        fields["sign"] = hashlib.md5(message.encode("utf-8")).hexdigest()
        assert verify_payu_confirmation_signature(fields, "4Vj8eK4rloUd272L48hsrarnUA")
