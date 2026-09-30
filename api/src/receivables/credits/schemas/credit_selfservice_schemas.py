"""Schema de respuesta de la solicitud de liquidación (settlement) de un crédito."""

from pydantic import Field

from core.base.schema_base import BaseSchema


class SettlementRequestResponse(BaseSchema):
    ticket_number: int = Field(description="Número del ticket de soporte creado")
    settlement_amount: float = Field(
        description="Monto total del crédito a saldar (snapshot de la solicitud)"
    )
