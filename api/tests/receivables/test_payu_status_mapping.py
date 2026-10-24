"""Mapeo de los dos vocabularios de estado de PayU a ReceivablesPaymentAttemptStatus."""

from receivables.payment_gateways.enums.payment_gateway_enums import (
    ReceivablesPaymentAttemptStatus,
)
from receivables.payment_gateways.utils.payu_status_mapping import (
    payu_state_pol_to_attempt_status,
    payu_transaction_state_to_attempt_status,
)


class TestPayuTransactionStateToAttemptStatus:
    def test_approved(self):
        assert (
            payu_transaction_state_to_attempt_status("APPROVED")
            == ReceivablesPaymentAttemptStatus.APPROVED
        )

    def test_declined(self):
        assert (
            payu_transaction_state_to_attempt_status("DECLINED")
            == ReceivablesPaymentAttemptStatus.DECLINED
        )

    def test_pending(self):
        assert (
            payu_transaction_state_to_attempt_status("PENDING")
            == ReceivablesPaymentAttemptStatus.PENDING
        )

    def test_expired_maps_to_error(self):
        assert (
            payu_transaction_state_to_attempt_status("EXPIRED")
            == ReceivablesPaymentAttemptStatus.ERROR
        )

    def test_unknown_state_maps_to_error(self):
        assert (
            payu_transaction_state_to_attempt_status("SOMETHING_NEW")
            == ReceivablesPaymentAttemptStatus.ERROR
        )


class TestPayuStatePolToAttemptStatus:
    def test_4_is_approved(self):
        assert (
            payu_state_pol_to_attempt_status("4")
            == ReceivablesPaymentAttemptStatus.APPROVED
        )

    def test_6_is_declined(self):
        assert (
            payu_state_pol_to_attempt_status("6")
            == ReceivablesPaymentAttemptStatus.DECLINED
        )

    def test_7_is_pending(self):
        assert (
            payu_state_pol_to_attempt_status("7")
            == ReceivablesPaymentAttemptStatus.PENDING
        )

    def test_5_is_error(self):
        assert (
            payu_state_pol_to_attempt_status("5")
            == ReceivablesPaymentAttemptStatus.ERROR
        )

    def test_unknown_code_maps_to_error(self):
        assert (
            payu_state_pol_to_attempt_status("99")
            == ReceivablesPaymentAttemptStatus.ERROR
        )
