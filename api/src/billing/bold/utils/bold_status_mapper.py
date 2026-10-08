"""Mapeo de estado de enlace de pago Bold a PaymentAttemptStatus interno."""

from billing.bold.enums.bold_enums import BoldLinkStatus
from billing.invoices.enums.invoice_enums import PaymentAttemptStatus

_BOLD_TO_ATTEMPT_STATUS: dict[BoldLinkStatus, PaymentAttemptStatus] = {
    BoldLinkStatus.ACTIVE: PaymentAttemptStatus.ACTIVE,
    BoldLinkStatus.PROCESSING: PaymentAttemptStatus.PROCESSING,
    BoldLinkStatus.PAID: PaymentAttemptStatus.PAID,
    BoldLinkStatus.EXPIRED: PaymentAttemptStatus.EXPIRED,
    BoldLinkStatus.REJECTED: PaymentAttemptStatus.REJECTED,
    BoldLinkStatus.CANCELLED: PaymentAttemptStatus.CANCELLED,
}


def bold_link_status_to_attempt_status(bold: BoldLinkStatus) -> PaymentAttemptStatus:
    """Mapeo explicito del estado de un enlace de pago Bold al
    PaymentAttemptStatus interno.
    """
    return _BOLD_TO_ATTEMPT_STATUS[bold]
