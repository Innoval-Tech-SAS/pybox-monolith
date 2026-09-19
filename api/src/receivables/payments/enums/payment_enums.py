from enum import StrEnum


class PaymentStatus(StrEnum):
    """Estado de una cuota/pago dentro del cronograma de un crédito.

    Flujo de autogestión del titular (rol USER, scope SELF) desde el calendario:
    - PENDING: estado por defecto de toda cuota cargada.
    - RESCHEDULE_REQUESTED: el titular pidió mover la fecha; hay un ticket
      "Reprogramación de pago" abierto para el CUSTOMER_SERVICE de la org dueña.
    - RESCHEDULED: el ticket fue aprobado; esta cuota queda cerrada y se creó una
      nueva cuota PENDING en la fecha elegida.
    - VALIDATION_REQUESTED: el titular subió un comprobante; hay un ticket
      "Validación de pago" abierto.
    - PAID: el pago fue validado/aprobado (el pago original se marca como realizado).
    """

    PENDING = "PENDIENTE"
    RESCHEDULE_REQUESTED = "REPROGRAMACION_SOLICITADA"
    RESCHEDULED = "REPROGRAMADO"
    VALIDATION_REQUESTED = "VALIDACION_SOLICITADA"
    PAID = "PAGADO"


# Nombre legible por código de estado — fuente de verdad expuesta por API
# (GET /payments/statuses) para el chip de "Detalle de obligaciones" del home del
# titular. El front no mantiene su propia copia. "Por vencer" es como el titular lee
# una cuota pendiente: el término interno es PENDING.
PAYMENT_STATUS_LABELS: dict[str, str] = {
    PaymentStatus.PENDING: "Por vencer",
    PaymentStatus.RESCHEDULE_REQUESTED: "Reprogramación solicitada",
    PaymentStatus.RESCHEDULED: "Reprogramado",
    PaymentStatus.VALIDATION_REQUESTED: "Validación solicitada",
    PaymentStatus.PAID: "Pagado",
}
