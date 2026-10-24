"""Catálogo de estados de pago (valores fijos derivados del enum)."""

from receivables.payments.enums.payment_enums import (
    PAYMENT_STATUS_LABELS,
    PaymentStatus,
)
from receivables.payments.schemas.payment_catalog_schemas import PaymentStatusOption


class PaymentCatalogService:
    """Catálogos de valores fijos del módulo de pagos.

    No toca base de datos: se arma desde el enum, que es la fuente de verdad.
    """

    def list_statuses(self) -> list[PaymentStatusOption]:
        return [
            PaymentStatusOption(value=status.value, label=PAYMENT_STATUS_LABELS[status])
            for status in PaymentStatus
        ]
