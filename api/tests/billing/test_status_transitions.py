"""Unitario puro (sin mocks, sin DB): billing/invoices/status_transitions.py son dos
funciones sincronas sin dependencias externas -- se ejercitan directo."""

import pytest

from billing.invoices.enums.invoice_enums import InvoiceStatus, PaymentAttemptStatus
from billing.invoices.status_transitions import (
    attempt_status_to_invoice_transition,
    is_attempt_reusable,
)

ALL_INVOICE_STATUSES = list(InvoiceStatus)


class TestAttemptStatusToInvoiceTransitionPaid:
    @pytest.mark.parametrize("current_invoice", ALL_INVOICE_STATUSES)
    def test_paid_attempt_always_transitions_invoice_to_paid(self, current_invoice):
        # Un intento PAID marca la factura como pagada sin importar en que estado
        # estuviera antes -- es la transicion que efectivamente mueve dinero.
        assert (
            attempt_status_to_invoice_transition(
                PaymentAttemptStatus.PAID, current_invoice
            )
            == InvoiceStatus.PAID
        )


class TestAttemptStatusToInvoiceTransitionActiveProcessing:
    @pytest.mark.parametrize(
        "attempt_status", [PaymentAttemptStatus.ACTIVE, PaymentAttemptStatus.PROCESSING]
    )
    @pytest.mark.parametrize(
        "current_invoice",
        [InvoiceStatus.ISSUED, InvoiceStatus.OVERDUE, InvoiceStatus.BLOCKED],
    )
    def test_transitions_to_payment_pending_from_open_states(
        self, attempt_status, current_invoice
    ):
        assert (
            attempt_status_to_invoice_transition(attempt_status, current_invoice)
            == InvoiceStatus.PAYMENT_PENDING
        )

    @pytest.mark.parametrize(
        "attempt_status", [PaymentAttemptStatus.ACTIVE, PaymentAttemptStatus.PROCESSING]
    )
    @pytest.mark.parametrize(
        "current_invoice",
        [
            InvoiceStatus.PAYMENT_PENDING,
            InvoiceStatus.PAID,
            InvoiceStatus.CANCELLED,
            InvoiceStatus.DRAFT,
        ],
    )
    def test_no_transition_from_non_open_states(self, attempt_status, current_invoice):
        # En particular PAID: un intento nuevo (ej. reintento manual) no debe poder
        # revertir una factura ya pagada a PAYMENT_PENDING.
        assert (
            attempt_status_to_invoice_transition(attempt_status, current_invoice)
            is None
        )


class TestAttemptStatusToInvoiceTransitionTerminalFailures:
    @pytest.mark.parametrize(
        "attempt_status",
        [
            PaymentAttemptStatus.EXPIRED,
            PaymentAttemptStatus.REJECTED,
            PaymentAttemptStatus.CANCELLED,
        ],
    )
    def test_reverts_payment_pending_to_issued(self, attempt_status):
        assert (
            attempt_status_to_invoice_transition(
                attempt_status, InvoiceStatus.PAYMENT_PENDING
            )
            == InvoiceStatus.ISSUED
        )

    @pytest.mark.parametrize(
        "attempt_status",
        [
            PaymentAttemptStatus.EXPIRED,
            PaymentAttemptStatus.REJECTED,
            PaymentAttemptStatus.CANCELLED,
        ],
    )
    @pytest.mark.parametrize(
        "current_invoice",
        [s for s in ALL_INVOICE_STATUSES if s != InvoiceStatus.PAYMENT_PENDING],
    )
    def test_no_transition_outside_payment_pending(
        self, attempt_status, current_invoice
    ):
        # Critico para PAID: un intento fallido/expirado/cancelado que llega tarde
        # (ej. el webhook de un intento viejo despues de que otro intento ya pago la
        # factura) no debe revertirla a ISSUED.
        assert (
            attempt_status_to_invoice_transition(attempt_status, current_invoice)
            is None
        )


class TestIsAttemptReusable:
    @pytest.mark.parametrize(
        "status", [PaymentAttemptStatus.ACTIVE, PaymentAttemptStatus.PROCESSING]
    )
    def test_reusable_statuses(self, status):
        assert is_attempt_reusable(status) is True

    @pytest.mark.parametrize(
        "status",
        [
            PaymentAttemptStatus.PAID,
            PaymentAttemptStatus.EXPIRED,
            PaymentAttemptStatus.REJECTED,
            PaymentAttemptStatus.CANCELLED,
        ],
    )
    def test_non_reusable_statuses(self, status):
        assert is_attempt_reusable(status) is False
