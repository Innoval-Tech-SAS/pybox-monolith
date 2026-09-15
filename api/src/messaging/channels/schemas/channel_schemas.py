import uuid
from decimal import Decimal
from datetime import datetime

from pydantic import Field

from core.base.schema_base import BaseSchema
from messaging.channels.enums.channel_enums import ChannelName, Currency


class ChannelCreateRequest(BaseSchema):
    name: ChannelName = Field(description="Nombre del canal")
    label: str = Field(description="Etiqueta visible del canal")
    currency: Currency = Field(default=Currency.COP, description="Moneda del canal")
    unit_price: Decimal = Field(description="Precio unitario por mensaje")
    description: str = Field(description="Descripción del canal")


class ChannelUpdateRequest(BaseSchema):
    label: str | None = Field(default=None, description="Nueva etiqueta")
    currency: Currency | None = Field(default=None, description="Nueva moneda")
    unit_price: Decimal | None = Field(default=None, description="Nuevo precio unitario")
    description: str | None = Field(default=None, description="Nueva descripción")


class ChannelResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID del canal")
    name: ChannelName = Field(description="Nombre del canal")
    label: str = Field(description="Etiqueta visible del canal")
    currency: Currency = Field(description="Moneda")
    unit_price: Decimal = Field(description="Precio unitario")
    description: str = Field(description="Descripción")
    created_at: datetime = Field(description="Fecha de creación")
    updated_at: datetime | None = Field(default=None, description="Fecha de actualización")
