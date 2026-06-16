import uuid
from datetime import datetime
from typing import Any

from pydantic import Field, model_validator

from base.schema_base import BaseSchema
from templates.enums.template_enums import TemplateChannel, TemplateStatus


class TemplateCreateRequest(BaseSchema):
    name: str = Field(description="Nombre de la plantilla")
    channel: TemplateChannel = Field(description="Canal: EMAIL o SMS")
    status: TemplateStatus = Field(default=TemplateStatus.DRAFT, description="Estado inicial")
    body: str = Field(description="Cuerpo del mensaje (HTML para email, texto para SMS)")
    subject: str | None = Field(default=None, description="Asunto del email (requerido para EMAIL)")
    sender_name: str | None = Field(default=None, description="Nombre del remitente")
    sender_email: str | None = Field(default=None, description="Email del remitente (requerido para EMAIL)")
    reply_to: str | None = Field(default=None, description="Dirección de respuesta (solo EMAIL)")

    @model_validator(mode="after")
    def validate_channel_fields(self) -> "TemplateCreateRequest":
        if self.channel == TemplateChannel.EMAIL:
            if not self.subject:
                raise ValueError("El campo 'subject' es obligatorio para plantillas de EMAIL")
            if not self.sender_email:
                raise ValueError("El campo 'senderEmail' es obligatorio para plantillas de EMAIL")
        if self.channel == TemplateChannel.SMS:
            if self.sender_email is not None:
                raise ValueError("El campo 'senderEmail' no aplica para plantillas de SMS")
            if self.reply_to is not None:
                raise ValueError("El campo 'replyTo' no aplica para plantillas de SMS")
        return self


class TemplateUpdateRequest(BaseSchema):
    name: str | None = Field(default=None, description="Nuevo nombre")
    status: TemplateStatus | None = Field(default=None, description="Nuevo estado")
    body: str | None = Field(default=None, description="Nuevo cuerpo del mensaje")
    subject: str | None = Field(default=None, description="Nuevo asunto")
    sender_name: str | None = Field(default=None, description="Nuevo nombre del remitente")
    sender_email: str | None = Field(default=None, description="Nuevo email del remitente")
    reply_to: str | None = Field(default=None, description="Nueva dirección de respuesta")


class TemplateResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID de la plantilla")
    organization_id: uuid.UUID = Field(description="ID de la organización")
    name: str = Field(description="Nombre de la plantilla")
    channel: TemplateChannel = Field(description="Canal de envío")
    status: TemplateStatus = Field(description="Estado de la plantilla")
    body: str = Field(description="Cuerpo del mensaje")
    subject: str | None = Field(default=None, description="Asunto del email")
    sender_name: str | None = Field(default=None, description="Nombre del remitente")
    sender_email: str | None = Field(default=None, description="Email del remitente")
    reply_to: str | None = Field(default=None, description="Dirección de respuesta")
    created_at: datetime = Field(description="Fecha de creación")
    updated_at: datetime | None = Field(default=None, description="Fecha de última actualización")


class TemplatePreviewRequest(BaseSchema):
    sub: dict[str, Any] = Field(default_factory=dict, description="Variables de sustitución")


class TemplatePreviewResponse(BaseSchema):
    html: str = Field(description="HTML renderizado con las variables sustituidas")
    subject: str = Field(description="Asunto renderizado")
    variables_used: list[str] = Field(description="Variables detectadas en la plantilla")


