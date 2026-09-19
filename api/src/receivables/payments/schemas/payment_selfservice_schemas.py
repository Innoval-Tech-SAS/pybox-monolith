from datetime import datetime

from pydantic import Field

from core.base.schema_base import BaseSchema


class RescheduleRequest(BaseSchema):
    new_date: datetime = Field(description="Nueva fecha de pago elegida por el titular (dentro de los próximos 30 días)")


class PaymentRequestResponse(BaseSchema):
    ticket_number: int = Field(description="Número del ticket de soporte creado")
    payment_status: str = Field(description="Nuevo estado del pago tras la solicitud")
