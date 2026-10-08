"""Schemas de plantillas de mensajería: alta, edición y variables disponibles."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import EmailStr, Field, model_validator

from core.base.schema_base import BaseSchema
from messaging.templates.enums.template_enums import TemplateChannel, TemplateStatus


class TemplateCreateRequest(BaseSchema):
    name: str = Field(description="Nombre de la plantilla")
    channel: TemplateChannel = Field(description="Canal: EMAIL, SMS o WHATSAPP")
    status: TemplateStatus = Field(
        default=TemplateStatus.DRAFT, description="Estado inicial"
    )
    body: str | None = Field(
        default=None,
        description=(
            "Cuerpo del mensaje (HTML para email, texto para SMS). No "
            "aplica para WHATSAPP"
        ),
    )
    design: str | None = Field(
        default=None,
        description="Diseño del editor visual de Unlayer en formato JSON (solo EMAIL)",
    )
    subject: str | None = Field(
        default=None, description="Asunto del email (requerido para EMAIL)"
    )
    sender_name: str | None = Field(default=None, description="Nombre del remitente")
    sender_email: str | None = Field(
        default=None, description="Email del remitente (requerido para EMAIL)"
    )
    reply_to: str | None = Field(
        default=None, description="Dirección de respuesta (solo EMAIL)"
    )

    @model_validator(mode="after")
    def validate_channel_fields(self) -> "TemplateCreateRequest":
        if self.channel == TemplateChannel.EMAIL:
            if not self.subject:
                raise ValueError(
                    "El campo 'subject' es obligatorio para plantillas de EMAIL"
                )
            if not self.sender_email:
                raise ValueError(
                    "El campo 'senderEmail' es obligatorio para plantillas de EMAIL"
                )
        if self.channel == TemplateChannel.SMS:
            if not self.body:
                raise ValueError(
                    "El campo 'body' es obligatorio para plantillas de SMS"
                )
            if self.sender_email is not None:
                raise ValueError(
                    "El campo 'senderEmail' no aplica para plantillas de SMS"
                )
            if self.reply_to is not None:
                raise ValueError("El campo 'replyTo' no aplica para plantillas de SMS")
        if self.channel == TemplateChannel.WHATSAPP:
            # El contenido real de una plantilla de WhatsApp se crea y aprueba en Meta
            # (ver datos_plantilla_whatsapp) — estos campos genéricos no aplican.
            if self.body is not None:
                raise ValueError(
                    "El campo 'body' no aplica para plantillas de "
                    "WHATSAPP (se crea en Meta)"
                )
            if self.design is not None:
                raise ValueError(
                    "El campo 'design' no aplica para plantillas de WHATSAPP"
                )
            if self.subject is not None:
                raise ValueError(
                    "El campo 'subject' no aplica para plantillas de WHATSAPP"
                )
            if self.sender_email is not None:
                raise ValueError(
                    "El campo 'senderEmail' no aplica para plantillas de WHATSAPP"
                )
            if self.reply_to is not None:
                raise ValueError(
                    "El campo 'replyTo' no aplica para plantillas de WHATSAPP"
                )
        return self


class TemplateUpdateRequest(BaseSchema):
    name: str | None = Field(default=None, description="Nuevo nombre")
    status: TemplateStatus | None = Field(default=None, description="Nuevo estado")
    body: str | None = Field(default=None, description="Nuevo cuerpo del mensaje")
    design: str | None = Field(
        default=None,
        description="Nuevo diseño del editor visual de Unlayer en formato JSON",
    )
    subject: str | None = Field(default=None, description="Nuevo asunto")
    sender_name: str | None = Field(
        default=None, description="Nuevo nombre del remitente"
    )
    sender_email: str | None = Field(
        default=None, description="Nuevo email del remitente"
    )
    reply_to: str | None = Field(
        default=None, description="Nueva dirección de respuesta"
    )


class TemplateResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID de la plantilla")
    portfolio_id: uuid.UUID = Field(description="ID del portafolio")
    name: str = Field(description="Nombre de la plantilla")
    channel: TemplateChannel = Field(description="Canal de envío")
    status: TemplateStatus = Field(description="Estado de la plantilla")
    body: str | None = Field(
        default=None, description="Cuerpo del mensaje (no aplica para WHATSAPP)"
    )
    design: str | None = Field(
        default=None, description="Diseño del editor visual de Unlayer en formato JSON"
    )
    subject: str | None = Field(default=None, description="Asunto del email")
    sender_name: str | None = Field(default=None, description="Nombre del remitente")
    sender_email: str | None = Field(default=None, description="Email del remitente")
    reply_to: str | None = Field(default=None, description="Dirección de respuesta")
    created_at: datetime = Field(description="Fecha de creación")
    updated_at: datetime | None = Field(
        default=None, description="Fecha de última actualización"
    )


class TemplateListResponse(BaseSchema):
    items: list[TemplateResponse] = Field(description="Plantillas de la página")
    total: int = Field(description="Total de registros")
    page: int = Field(description="Página actual")
    page_size: int = Field(description="Tamaño de página")


class TemplatePreviewRequest(BaseSchema):
    sub: dict[str, Any] = Field(
        default_factory=dict, description="Variables de sustitución"
    )


class TemplatePreviewResponse(BaseSchema):
    html: str = Field(description="HTML renderizado con las variables sustituidas")
    subject: str = Field(description="Asunto renderizado")
    variables_used: list[str] = Field(
        description="Variables detectadas en la plantilla"
    )


class TemplateSendRequest(BaseSchema):
    to: EmailStr = Field(description="Destinatario del envío")
    subject: str | None = Field(
        default=None,
        description="Asunto personalizado (si no, se usa el de la plantilla)",
    )
    sub: dict[str, Any] = Field(
        default_factory=dict, description="Variables de sustitución"
    )


class TemplateSendResponse(BaseSchema):
    message: str = Field(description="Resultado del envío")


class TemplateVariableOption(BaseSchema):
    key: str = Field(
        description="Clave de la variable, usada como {key} en el cuerpo del mensaje"
    )
    label: str = Field(description="Etiqueta legible para mostrar en el editor")
    example: str = Field(description="Valor de ejemplo usado en la vista previa")
    source_table: str = Field(
        description="Tabla de origen de la columna, usada para resolverla al enviar"
    )
