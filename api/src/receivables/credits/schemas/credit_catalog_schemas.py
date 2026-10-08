"""Schema del catálogo de tipos de crédito."""

from pydantic import Field

from core.base.schema_base import BaseSchema


class CreditTypeOption(BaseSchema):
    """Opción de tipo de crédito para los selects y etiquetas del front, que no
    mantiene su propia lista ni sus textos legibles."""

    value: str = Field(
        description="Código del tipo de crédito (tarjeta_credito, credito_vehiculo, …)"
    )
    label: str = Field(
        description="Etiqueta para mostrar (p. ej. 'Tarjeta de crédito')"
    )
