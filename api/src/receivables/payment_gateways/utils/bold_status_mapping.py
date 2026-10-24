"""Mapeo de estado de pago de Bold a ReceivablesPaymentAttemptStatus."""

from receivables.payment_gateways.enums.payment_gateway_enums import (
    ReceivablesPaymentAttemptStatus,
)

_BOLD_TO_ATTEMPT_STATUS = {
    "APPROVED": ReceivablesPaymentAttemptStatus.APPROVED,
    "REJECTED": ReceivablesPaymentAttemptStatus.DECLINED,
    "FAILED": ReceivablesPaymentAttemptStatus.ERROR,
    "VOIDED": ReceivablesPaymentAttemptStatus.VOIDED,
    "PROCESSING": ReceivablesPaymentAttemptStatus.PENDING,
    "PENDING": ReceivablesPaymentAttemptStatus.PENDING,
    "RUNNING": ReceivablesPaymentAttemptStatus.PENDING,
    # Bold todavia no registro ningun intento de pago contra el intent (el deudor aun
    # no volvio de la redireccion) -- se trata como pendiente, no como error, para que
    # el polling del frontend siga reintentando.
    "NO_TRANSACTION_FOUND": ReceivablesPaymentAttemptStatus.PENDING,
}


def bold_status_to_attempt_status(bold_status: str) -> ReceivablesPaymentAttemptStatus:
    """Vocabulario propio de Bold (ver developers.bold.co/pagos-en-linea/
    consulta-de-transacciones), distinto al de `ReceivablesPaymentAttemptStatus` -- a
    diferencia de Wompi, que ya usa el mismo vocabulario (ver `wompi_status_mapping`),
    aqui hace falta una traduccion explicita."""
    return _BOLD_TO_ATTEMPT_STATUS.get(
        bold_status, ReceivablesPaymentAttemptStatus.ERROR
    )
