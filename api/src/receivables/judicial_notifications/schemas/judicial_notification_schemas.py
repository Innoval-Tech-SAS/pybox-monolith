"""Schemas de notificaciones judiciales: alta, buzón del deudor y panel de entidad."""

import uuid
from datetime import datetime

from pydantic import Field

from core.base.schema_base import BaseSchema
from receivables.credits.enums.credit_enums import CreditTypes
from receivables.judicial_notifications.enums.judicial_notification_enums import (
    JudicialPriority,
)


class JudicialPriorityOption(BaseSchema):
    """Opción de prioridad para el select del panel de la entidad y el chip del
    buzón."""

    value: str = Field(
        description="Código de la prioridad (urgente, media, baja, informativa)"
    )
    label: str = Field(description="Etiqueta para mostrar (p. ej. 'Urgente')")


class JudicialNotificationCreate(BaseSchema):
    credit_id: uuid.UUID = Field(
        description="Crédito sobre el que se emite la notificación"
    )
    title: str = Field(
        min_length=1, max_length=255, description="Título de la notificación"
    )
    body: str = Field(
        min_length=1, max_length=1000, description="Detalle de la notificación"
    )
    priority: JudicialPriority = Field(description="Urgencia de la notificación")
    notified_at: datetime | None = Field(
        default=None,
        description=(
            "Fecha del hecho judicial. Si se omite, se usa la fecha de captura."
        ),
    )


class JudicialNotificationAttachment(BaseSchema):
    id: uuid.UUID = Field(description="ID del documento adjunto")
    name: str = Field(description="Nombre del archivo")
    url: str = Field(description="URL de descarga")
    size: int = Field(description="Tamaño en bytes")


class JudicialNotificationResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID de la notificación")
    title: str = Field(description="Título")
    body: str = Field(description="Detalle")
    priority: JudicialPriority = Field(description="Urgencia")
    is_read: bool = Field(description="Si el titular ya la leyó")
    notified_at: datetime = Field(description="Fecha del hecho judicial")
    credit_id: uuid.UUID = Field(description="Crédito al que corresponde")
    credit_number: str = Field(description="Número del crédito")
    credit_type: CreditTypes = Field(description="Tipo de crédito")
    entity_name: str = Field(description="Nombre de la entidad acreedora")
    attachments: list[JudicialNotificationAttachment] = Field(
        default_factory=list, description="Soporte documental adjunto por la entidad"
    )


class JudicialInboxResponse(BaseSchema):
    """Buzón del titular: las notificaciones más el contador que pinta el badge."""

    items: list[JudicialNotificationResponse] = Field(
        description="Notificaciones, de la más reciente a la más antigua"
    )
    unread_count: int = Field(description="Cantidad de notificaciones sin leer")
