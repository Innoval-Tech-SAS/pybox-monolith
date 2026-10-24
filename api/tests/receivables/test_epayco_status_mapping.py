"""Mapeo del vocabulario de estado de ePayco a ReceivablesPaymentAttemptStatus."""

from receivables.payment_gateways.enums.payment_gateway_enums import (
    ReceivablesPaymentAttemptStatus,
)
from receivables.payment_gateways.utils.epayco_status_mapping import (
    epayco_status_to_attempt_status,
)


class TestEpaycoStatusToAttemptStatus:
    def test_aceptada_is_approved(self):
        assert (
            epayco_status_to_attempt_status("Aceptada")
            == ReceivablesPaymentAttemptStatus.APPROVED
        )

    def test_rechazada_is_declined(self):
        assert (
            epayco_status_to_attempt_status("Rechazada")
            == ReceivablesPaymentAttemptStatus.DECLINED
        )

    def test_pendiente_is_pending(self):
        assert (
            epayco_status_to_attempt_status("Pendiente")
            == ReceivablesPaymentAttemptStatus.PENDING
        )

    def test_fallida_is_error(self):
        assert (
            epayco_status_to_attempt_status("Fallida")
            == ReceivablesPaymentAttemptStatus.ERROR
        )

    def test_reversada_is_voided(self):
        assert (
            epayco_status_to_attempt_status("Reversada")
            == ReceivablesPaymentAttemptStatus.VOIDED
        )

    def test_caducada_is_error(self):
        assert (
            epayco_status_to_attempt_status("caducada")
            == ReceivablesPaymentAttemptStatus.ERROR
        )

    def test_unknown_status_maps_to_error(self):
        assert (
            epayco_status_to_attempt_status("SOMETHING_NEW")
            == ReceivablesPaymentAttemptStatus.ERROR
        )
