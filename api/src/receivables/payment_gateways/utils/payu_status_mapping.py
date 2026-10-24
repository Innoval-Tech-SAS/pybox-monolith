"""Mapeo de estado de PayU a ReceivablesPaymentAttemptStatus.

PayU reporta el estado con DOS vocabularios distintos según el canal: la respuesta
síncrona de `SUBMIT_TRANSACTION`/`ORDER_DETAIL_BY_REFERENCE_CODE` usa texto
(`transactionResponse.state`); la confirmación (`notifyUrl`) usa el código numérico
`state_pol` -- ninguno coincide con el vocabulario propio de
`ReceivablesPaymentAttemptStatus`, a diferencia de Wompi (ver `wompi_status_mapping`),
así que hacen falta dos traducciones explícitas."""

from receivables.payment_gateways.enums.payment_gateway_enums import (
    ReceivablesPaymentAttemptStatus,
)

_TRANSACTION_STATE_TO_ATTEMPT_STATUS = {
    "APPROVED": ReceivablesPaymentAttemptStatus.APPROVED,
    "DECLINED": ReceivablesPaymentAttemptStatus.DECLINED,
    "PENDING": ReceivablesPaymentAttemptStatus.PENDING,
    "ERROR": ReceivablesPaymentAttemptStatus.ERROR,
    # Sin equivalente propio -- un pago PSE caducado (el deudor no confirmó en el
    # banco) no es un error de integración, pero tampoco queda PENDING para siempre.
    "EXPIRED": ReceivablesPaymentAttemptStatus.ERROR,
}

_STATE_POL_TO_ATTEMPT_STATUS = {
    "4": ReceivablesPaymentAttemptStatus.APPROVED,
    "6": ReceivablesPaymentAttemptStatus.DECLINED,
    "5": ReceivablesPaymentAttemptStatus.ERROR,  # expirada
    "7": ReceivablesPaymentAttemptStatus.PENDING,
}


def payu_transaction_state_to_attempt_status(
    state: str,
) -> ReceivablesPaymentAttemptStatus:
    """Para `transactionResponse.state` (respuesta directa de `SUBMIT_TRANSACTION` y
    de la consulta `ORDER_DETAIL_BY_REFERENCE_CODE`, ver `PayUGateway.get_transaction`).
    """
    return _TRANSACTION_STATE_TO_ATTEMPT_STATUS.get(
        state, ReceivablesPaymentAttemptStatus.ERROR
    )


def payu_state_pol_to_attempt_status(state_pol: str) -> ReceivablesPaymentAttemptStatus:
    """Para el `state_pol` de la confirmación (`notifyUrl`) -- ver
    `PayUWebhookService`."""
    return _STATE_POL_TO_ATTEMPT_STATUS.get(
        state_pol, ReceivablesPaymentAttemptStatus.ERROR
    )
