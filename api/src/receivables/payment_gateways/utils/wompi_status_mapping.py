"""Mapeo de estado de transacción de Wompi a ReceivablesPaymentAttemptStatus."""

from receivables.payment_gateways.enums.payment_gateway_enums import (
    PaymentSourceStatus,
    ReceivablesPaymentAttemptStatus,
)


def to_attempt_status(wompi_status: str) -> ReceivablesPaymentAttemptStatus:
    """Wompi ya usa PENDING/APPROVED/DECLINED/ERROR/VOIDED para transacciones — mismo
    vocabulario que `ReceivablesPaymentAttemptStatus`, esto solo blinda contra un valor
    nuevo/desconocido que la doc todavia no liste."""
    try:
        return ReceivablesPaymentAttemptStatus(wompi_status)
    except ValueError:
        return ReceivablesPaymentAttemptStatus.ERROR


def to_source_status(wompi_status: str) -> PaymentSourceStatus:
    try:
        return PaymentSourceStatus(wompi_status)
    except ValueError:
        return PaymentSourceStatus.ERROR
