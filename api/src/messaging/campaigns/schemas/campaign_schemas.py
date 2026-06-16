import uuid
from datetime import datetime

from pydantic import Field

from core.base.schema_base import BaseSchema
from messaging.campaigns.enums.campaign_enums import CampaignStatus, Periodicity


class CampaignResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID de la campaña")
    organization_id: uuid.UUID = Field(description="ID de la organización")
    name: str = Field(description="Nombre de la campaña")
    message: str = Field(description="Mensaje de la campaña")
    subject: str | None = Field(default=None, description="Asunto del mensaje")
    channel: str = Field(description="Canal de envío")
    description: str | None = Field(default=None, description="Descripción de la campaña")
    status: CampaignStatus = Field(description="Estado de la campaña")
    total_recipients: int = Field(description="Total de destinatarios")
    scheduled_at: datetime | None = Field(default=None, description="Fecha y hora programada")
    timezone: str = Field(description="Zona horaria de la campaña")
    fallback: bool = Field(description="Indica si se usa canal de fallback")
    segment_id: uuid.UUID | None = Field(default=None, description="ID del segmento de destinatarios")
    template_id: uuid.UUID | None = Field(default=None, description="ID de la plantilla de mensaje")
    periodicity: Periodicity | None = Field(default=None, description="Periodicidad de ejecución")
    time_to_send: str | None = Field(default=None, description="Hora de envío HH:MM")
    is_immediate: bool = Field(default=False, description="Enviar inmediatamente al activar")
    days_of_week: list[int] | None = Field(
        default=None, description="Días de la semana para periodicidad weekly (0=domingo..6=sábado)"
    )
    created_at: datetime = Field(description="Fecha de creación")
    updated_at: datetime | None = Field(default=None, description="Fecha de última actualización")


class CampaignCreateRequest(BaseSchema):
    name: str = Field(description="Nombre de la campaña")
    message: str = Field(description="Mensaje de la campaña")
    subject: str | None = Field(default=None, description="Asunto del mensaje")
    channel: str = Field(default="auto", description="Canal de envío")
    description: str | None = Field(default=None, description="Descripción de la campaña")
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT, description="Estado inicial")
    total_recipients: int = Field(default=0, description="Total de destinatarios")
    scheduled_at: datetime | None = Field(default=None, description="Fecha y hora programada")
    timezone: str = Field(default="UTC", description="Zona horaria")
    fallback: bool = Field(default=True, description="Usar canal de fallback")
    segment_id: uuid.UUID | None = Field(default=None, description="ID del segmento")
    template_id: uuid.UUID | None = Field(default=None, description="ID de la plantilla")
    periodicity: Periodicity | None = Field(default=None, description="Periodicidad")
    time_to_send: str | None = Field(default=None, description="Hora HH:MM para campañas recurrentes")
    is_immediate: bool = Field(default=False, description="Enviar inmediatamente al activar")
    days_of_week: list[int] | None = Field(
        default=None, description="Días de la semana para periodicidad weekly (0=domingo..6=sábado)"
    )


class CampaignUpdateRequest(BaseSchema):
    name: str | None = Field(default=None, description="Nuevo nombre")
    message: str | None = Field(default=None, description="Nuevo mensaje")
    subject: str | None = Field(default=None, description="Nuevo asunto")
    channel: str | None = Field(default=None, description="Nuevo canal")
    description: str | None = Field(default=None, description="Nueva descripción")
    status: CampaignStatus | None = Field(default=None, description="Nuevo estado")
    total_recipients: int | None = Field(default=None, description="Total de destinatarios")
    scheduled_at: datetime | None = Field(default=None, description="Nueva fecha programada")
    timezone: str | None = Field(default=None, description="Nueva zona horaria")
    fallback: bool | None = Field(default=None, description="Usar canal de fallback")
    segment_id: uuid.UUID | None = Field(default=None, description="ID del segmento")
    template_id: uuid.UUID | None = Field(default=None, description="ID de la plantilla")
    periodicity: Periodicity | None = Field(default=None, description="Periodicidad")
    time_to_send: str | None = Field(default=None, description="Hora HH:MM")
    is_immediate: bool | None = Field(default=None, description="Enviar inmediatamente")
    days_of_week: list[int] | None = Field(
        default=None, description="Días de la semana para periodicidad weekly (0=domingo..6=sábado)"
    )
