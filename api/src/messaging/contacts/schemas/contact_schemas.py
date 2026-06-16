import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import Field

from core.base.schema_base import BaseSchema
from messaging.contacts.enums.contact_enums import ContactStatus


class ContactResponse(BaseSchema):
    id: int = Field(description="ID del contacto")
    content: str = Field(description="Contenido enviado")
    recipient: str = Field(description="Destinatario (email o teléfono)")
    status: ContactStatus = Field(description="Estado del contacto")
    debtor_id: int | None = Field(default=None)
    debtor_document: str | None = Field(default=None)
    sent_at: datetime | None = Field(default=None)
    provider_id: str | None = Field(default=None)
    error: str | None = Field(default=None)
    campaign_id: uuid.UUID | None = Field(default=None)
    organization_id: uuid.UUID | None = Field(default=None)
    portfolio_id: uuid.UUID | None = Field(default=None)
    snapshot_channel_id: int | None = Field(default=None)
    snapshot_currency: str | None = Field(default=None)
    snapshot_unit_price: Decimal | None = Field(default=None)
    created_at: datetime = Field(description="Fecha de creación")


class ContactsByChannelGroup(BaseSchema):
    channel_id: int | None = Field(description="ID del canal")
    channel_name: str = Field(description="Nombre del canal")
    total: int = Field(description="Total de contactos en este canal")
    items: list[ContactResponse] = Field(description="Registros del canal")
