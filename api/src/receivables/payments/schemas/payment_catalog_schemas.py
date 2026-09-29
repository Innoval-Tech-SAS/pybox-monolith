from pydantic import Field

from core.base.schema_base import BaseSchema


class PaymentStatusOption(BaseSchema):
    """Opción de estado de pago para los chips y filtros del front, que no mantiene
    su propia lista ni sus textos legibles."""

    value: str = Field(
        description="Código del estado (pendiente, reprogramado, pagado, …)"
    )
    label: str = Field(description="Etiqueta para mostrar (p. ej. 'Por vencer')")
