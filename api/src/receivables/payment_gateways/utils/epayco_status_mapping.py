"""Mapeo de estado de ePayco a ReceivablesPaymentAttemptStatus.

A diferencia de PayU (ver `payu_status_mapping`), ePayco usa el MISMO vocabulario de
texto (`estado`/`status`/`x_transaction_state`/`x_response`) tanto en la respuesta
síncrona de creación/confirmación como en la confirmación por `notifyUrl` -- una sola
traducción basta (confirmada contra docs.epayco.com/docs/checkout-respuesta-y-
confirmacion, tabla "Códigos de respuesta")."""

from receivables.payment_gateways.enums.payment_gateway_enums import (
    ReceivablesPaymentAttemptStatus,
)

_STATUS_TO_ATTEMPT_STATUS = {
    "Aceptada": ReceivablesPaymentAttemptStatus.APPROVED,
    "Rechazada": ReceivablesPaymentAttemptStatus.DECLINED,
    "Pendiente": ReceivablesPaymentAttemptStatus.PENDING,
    "Fallida": ReceivablesPaymentAttemptStatus.ERROR,
    # Reintegro al pagador -- mismo significado que el VOIDED de Wompi.
    "Reversada": ReceivablesPaymentAttemptStatus.VOIDED,
    "retenida": ReceivablesPaymentAttemptStatus.PENDING,
    "iniciada": ReceivablesPaymentAttemptStatus.PENDING,
    # Caducada/abandonada: el deudor nunca terminó el flujo -- no es un error de
    # integración, pero tampoco puede quedar PENDING para siempre (mismo criterio que
    # el EXPIRED de PayU).
    "caducada": ReceivablesPaymentAttemptStatus.ERROR,
    "abandonada": ReceivablesPaymentAttemptStatus.ERROR,
    "Cancelada": ReceivablesPaymentAttemptStatus.DECLINED,
}


def epayco_status_to_attempt_status(status: str) -> ReceivablesPaymentAttemptStatus:
    return _STATUS_TO_ATTEMPT_STATUS.get(status, ReceivablesPaymentAttemptStatus.ERROR)
