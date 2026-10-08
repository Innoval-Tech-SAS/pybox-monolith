"""Schemas de chats y mensajes de WhatsApp."""

import uuid
from datetime import datetime

from pydantic import Field

from core.base.schema_base import BaseSchema
from messaging.campaigns.enums.campaign_enums import CampaignStatus
from messaging.whatsapp.enums.whatsapp_enums import MessageDirection
from receivables.debtors.schemas.debtor_schemas import (
    DebtorCreditResponse,
    DebtorResponse,
)


class WhatsAppChatResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID del hilo")
    organization_id: uuid.UUID = Field(description="Organización dueña del hilo")
    organization_name: str = Field(
        default="", description="Nombre de la organización dueña del hilo"
    )
    phone: str = Field(description="Teléfono del deudor")
    profile_name: str | None = Field(
        default=None,
        description="Nombre de perfil de WhatsApp (no es el nombre real del deudor)",
    )
    debtor_id: uuid.UUID | None = Field(
        default=None, description="Deudor asociado, si hay match"
    )
    portfolio_id: uuid.UUID | None = Field(
        default=None, description="Portafolio de origen del hilo, si se pudo resolver"
    )
    campaign_id: uuid.UUID | None = Field(
        default=None, description="Campaña de origen del hilo, si se pudo resolver"
    )
    assigned_user_id: uuid.UUID | None = Field(
        default=None, description="Agente de WhatsApp asignado"
    )
    last_message_at: datetime | None = Field(
        default=None, description="Fecha del último mensaje del hilo"
    )
    created_at: datetime = Field(description="Fecha de creación del hilo")


class WhatsAppChatListResponse(BaseSchema):
    items: list[WhatsAppChatResponse] = Field(description="Hilos de la página")
    total: int = Field(description="Total de registros")
    page: int = Field(description="Página actual")
    page_size: int = Field(description="Tamaño de página")


class WhatsAppChatAssignRequest(BaseSchema):
    assigned_user_id: uuid.UUID = Field(
        description="Usuario al que se reasigna el hilo"
    )


class WhatsAppMessageResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID del mensaje")
    chat_id: uuid.UUID = Field(description="Hilo al que pertenece")
    direction: MessageDirection = Field(description="ENTRANTE o SALIENTE")
    wamid: str | None = Field(default=None, description="ID del mensaje en Meta")
    message_type: str = Field(
        description="Tipo de mensaje (text/button/interactive/...)"
    )
    content: str | None = Field(
        default=None, description="Contenido o descripción del mensaje"
    )
    sent_at: datetime = Field(description="Fecha del mensaje")


class WhatsAppSendMessageRequest(BaseSchema):
    body: str = Field(
        min_length=1, max_length=4096, description="Texto libre a enviar al deudor"
    )


class WhatsAppChatPortfolioInfo(BaseSchema):
    id: uuid.UUID = Field(description="ID del portafolio")
    name: str = Field(description="Nombre del portafolio")


class WhatsAppChatCampaignInfo(BaseSchema):
    id: uuid.UUID = Field(description="ID de la campaña")
    name: str = Field(description="Nombre de la campaña")
    status: CampaignStatus = Field(description="Estado de la campaña")


class WhatsAppChatDetailsResponse(BaseSchema):
    debtor: DebtorResponse | None = Field(
        default=None, description="Deudor asociado al hilo, si hay match"
    )
    is_self_registered: bool = Field(
        default=False,
        description=(
            "Si el deudor tiene una cuenta propia (usuario SELF) en la plataforma"
        ),
    )
    portfolio: WhatsAppChatPortfolioInfo | None = Field(
        default=None, description="Portafolio de origen del hilo"
    )
    campaign: WhatsAppChatCampaignInfo | None = Field(
        default=None, description="Campaña de origen del hilo"
    )
    credits: list[DebtorCreditResponse] = Field(
        default_factory=list,
        description="Créditos del deudor en el portafolio de origen",
    )
