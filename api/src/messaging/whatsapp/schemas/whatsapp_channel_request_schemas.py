import uuid
from datetime import datetime

from pydantic import Field

from core.base.schema_base import BaseSchema
from messaging.whatsapp.enums.whatsapp_enums import ChannelRequestStatus


class WhatsAppChannelRequestResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID de la solicitud")
    phone: str = Field(description="Teléfono solicitado")
    debtor_id: uuid.UUID | None = Field(
        default=None, description="Deudor asociado, si hay match"
    )
    status: ChannelRequestStatus = Field(description="Estado de la solicitud")
    origin_campaign_id: uuid.UUID | None = Field(
        default=None, description="Campaña que originó la solicitud"
    )
    resolved_by: uuid.UUID | None = Field(
        default=None, description="Usuario que aprobó/rechazó"
    )
    resolved_at: datetime | None = Field(
        default=None, description="Fecha de resolución"
    )
    created_at: datetime = Field(description="Fecha de creación de la solicitud")


class WhatsAppChannelRequestListResponse(BaseSchema):
    items: list[WhatsAppChannelRequestResponse] = Field(
        description="Solicitudes de la página"
    )
    total: int = Field(description="Total de registros")
    page: int = Field(description="Página actual")
    page_size: int = Field(description="Tamaño de página")
