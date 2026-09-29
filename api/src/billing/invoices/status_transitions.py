from billing.invoices.enums.invoice_enums import InvoiceStatus, PaymentAttemptStatus


def attempt_status_to_invoice_transition(
    attempt: PaymentAttemptStatus,
    current_invoice: InvoiceStatus,
) -> InvoiceStatus | None:
    """Deriva el nuevo InvoiceStatus a partir del resultado de un intento de
    pago, sin importar el proveedor.
    """
    if attempt == PaymentAttemptStatus.PAID:
        return InvoiceStatus.PAID

    if attempt in (PaymentAttemptStatus.ACTIVE, PaymentAttemptStatus.PROCESSING):
        if current_invoice in (
            InvoiceStatus.ISSUED,
            InvoiceStatus.OVERDUE,
            InvoiceStatus.BLOCKED,
        ):
            return InvoiceStatus.PAYMENT_PENDING
        return None

    if attempt in (
        PaymentAttemptStatus.EXPIRED,
        PaymentAttemptStatus.REJECTED,
        PaymentAttemptStatus.CANCELLED,
    ):
        # Revertir PAYMENT_PENDING a ISSUED; el cron diario reevalua OVERDUE/BLOCKED.
        if current_invoice == InvoiceStatus.PAYMENT_PENDING:
            return InvoiceStatus.ISSUED
        return None

    return None


def is_attempt_reusable(status: PaymentAttemptStatus) -> bool:
    """True si un intento existente puede reutilizarse (el enlace sigue activo)."""
    return status in (PaymentAttemptStatus.ACTIVE, PaymentAttemptStatus.PROCESSING)
