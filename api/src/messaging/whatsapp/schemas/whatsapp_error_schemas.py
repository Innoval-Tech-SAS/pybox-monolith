import uuid
from datetime import datetime

from pydantic import Field

from core.base.schema_base import BaseSchema


class WhatsAppSendErrorResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID del error")
    contact_id: uuid.UUID | None = Field(
        default=None, description="Contacto asociado, si hubo match"
    )
    wamid: str | None = Field(
        default=None,
        description=(
            "ID del mensaje de Meta, si el error está asociado a un envío puntual"
        ),
    )
    error_code: int = Field(description="Código de error de Meta")
    error_subcode: int | None = Field(
        default=None,
        description="Subcódigo de error de Meta (deprecado por Meta desde v16.0)",
    )
    error_type: str | None = Field(
        default=None, description="Tipo de error (campo 'type' de Meta)"
    )
    message: str = Field(
        description="Mensaje del error (incluye el título, ej. '(#131047) ...')"
    )
    details: str | None = Field(default=None, description="Detalle adicional del error")
    fbtrace_id: str | None = Field(
        default=None, description="ID de rastreo de Meta, útil para soporte"
    )
    occurred_at: datetime = Field(description="Fecha del evento, según Meta")


class WhatsAppSendErrorListResponse(BaseSchema):
    items: list[WhatsAppSendErrorResponse] = Field(description="Errores de la página")
    total: int = Field(description="Total de registros")
    page: int = Field(description="Página actual")
    page_size: int = Field(description="Tamaño de página")
