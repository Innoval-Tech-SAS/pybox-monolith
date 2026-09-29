import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import Field

from core.base.schema_base import BaseSchema
from messaging.contacts.enums.contact_enums import ContactStatus


class ContactResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID del contacto")
    content: str = Field(description="Contenido enviado")
    recipient: str = Field(description="Destinatario (email o teléfono)")
    status: ContactStatus = Field(description="Estado del contacto")
    debtor_id: uuid.UUID | None = Field(
        default=None, description="ID del deudor relacionado"
    )
    debtor_document: str | None = Field(
        default=None, description="Número de documento del deudor"
    )
    sent_at: datetime | None = Field(default=None, description="Fecha y hora de envío")
    external_id: str | None = Field(
        default=None,
        description=(
            "ID individual del mensaje en el proveedor (NRS360), usado para el webhook"
        ),
    )
    error: str | None = Field(
        default=None, description="Mensaje de error si el envío falló"
    )
    campaign_id: uuid.UUID | None = Field(
        default=None, description="ID de la campaña que originó el envío"
    )
    organization_id: uuid.UUID | None = Field(
        default=None, description="ID de la organización"
    )
    portfolio_id: uuid.UUID | None = Field(
        default=None, description="ID del portafolio"
    )
    snapshot_channel_id: uuid.UUID | None = Field(
        default=None, description="ID del canal usado, capturado al momento del envío"
    )
    snapshot_currency: str | None = Field(
        default=None, description="Moneda del canal, capturada al momento del envío"
    )
    snapshot_unit_price: Decimal | None = Field(
        default=None,
        description="Precio unitario del canal, capturado al momento del envío",
    )
    created_at: datetime = Field(description="Fecha de creación")


class ContactsByChannelGroup(BaseSchema):
    channel_id: uuid.UUID | None = Field(description="ID del canal")
    channel_name: str = Field(description="Nombre del canal")
    total: int = Field(description="Total de envíos en este canal")
    page: int = Field(description="Página actual")
    page_size: int = Field(description="Tamaño de página")
    total_pages: int = Field(description="Total de páginas para este canal")
    items: list[ContactResponse] = Field(
        description="Envíos del canal en la página actual"
    )
