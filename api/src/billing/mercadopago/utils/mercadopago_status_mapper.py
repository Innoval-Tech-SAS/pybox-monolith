"""Mapeo de estado de Order de Mercado Pago a PaymentAttemptStatus interno."""

from billing.invoices.enums.invoice_enums import PaymentAttemptStatus
from billing.mercadopago.enums.mercadopago_enums import MercadoPagoOrderStatus

_ORDER_TO_ATTEMPT_STATUS: dict[MercadoPagoOrderStatus, PaymentAttemptStatus] = {
    MercadoPagoOrderStatus.CREATED: PaymentAttemptStatus.ACTIVE,
    MercadoPagoOrderStatus.PROCESSING: PaymentAttemptStatus.PROCESSING,
    MercadoPagoOrderStatus.ACTION_REQUIRED: PaymentAttemptStatus.PROCESSING,
    MercadoPagoOrderStatus.PROCESSED: PaymentAttemptStatus.PAID,
    MercadoPagoOrderStatus.CANCELED: PaymentAttemptStatus.CANCELLED,
    MercadoPagoOrderStatus.EXPIRED: PaymentAttemptStatus.EXPIRED,
    MercadoPagoOrderStatus.FAILED: PaymentAttemptStatus.REJECTED,
}


def mercadopago_order_status_to_attempt_status(
    order_status: str,
) -> PaymentAttemptStatus | None:
    """
    None para REFUNDED/CHARGED_BACK y cualquier status no mapeado: la factura ya
    quedo PAID antes de un reembolso/contracargo, su manejo es un caso aparte
    (nota de credito / disputa), no una transicion de PaymentAttemptStatus.
    """
    try:
        status = MercadoPagoOrderStatus(order_status)
    except ValueError:
        return None
    return _ORDER_TO_ATTEMPT_STATUS.get(status)
