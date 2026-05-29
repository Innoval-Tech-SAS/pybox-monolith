import uuid
from datetime import datetime

from pydantic import Field

from base.schema_base import BaseSchema
from payment_methods.enums.payment_method_enums import PaymentMethodType


class PaymentMethodResponse(BaseSchema):
    id: int = Field(description="ID del método de pago")
    organization_id: uuid.UUID = Field(description="ID de la organización")
    name: str = Field(description="Nombre del método de pago")
    type: PaymentMethodType = Field(description="Tipo de método de pago")
    description: str | None = Field(default=None, description="Descripción")
    instructions: str | None = Field(default=None, description="Instrucciones de pago")
    bank_name: str | None = Field(default=None, description="Nombre del banco")
    account_type: str | None = Field(default=None, description="Tipo de cuenta")
    account_number: str | None = Field(default=None, description="Número de cuenta")
    payment_link: str | None = Field(default=None, description="Enlace de pago")
    qr_image_url: str | None = Field(default=None, description="URL de imagen QR")
    is_active: bool = Field(description="Indica si el método está activo")
    created_at: datetime = Field(description="Fecha de creación")
    updated_at: datetime | None = Field(default=None, description="Fecha de actualización")


class PaymentMethodCreateRequest(BaseSchema):
    organization_id: uuid.UUID = Field(description="ID de la organización")
    name: str = Field(description="Nombre del método de pago")
    type: PaymentMethodType = Field(description="Tipo de método de pago")
    description: str | None = Field(default=None, description="Descripción")
    instructions: str | None = Field(default=None, description="Instrucciones de pago")
    bank_name: str | None = Field(default=None, description="Nombre del banco")
    account_type: str | None = Field(default=None, description="Tipo de cuenta")
    account_number: str | None = Field(default=None, description="Número de cuenta")
    payment_link: str | None = Field(default=None, description="Enlace de pago")
    qr_image_url: str | None = Field(default=None, description="URL de imagen QR")


class PaymentMethodUpdateRequest(BaseSchema):
    name: str | None = Field(default=None, description="Nombre del método de pago")
    type: PaymentMethodType | None = Field(default=None, description="Tipo de método de pago")
    description: str | None = Field(default=None, description="Descripción")
    instructions: str | None = Field(default=None, description="Instrucciones de pago")
    bank_name: str | None = Field(default=None, description="Nombre del banco")
    account_type: str | None = Field(default=None, description="Tipo de cuenta")
    account_number: str | None = Field(default=None, description="Número de cuenta")
    payment_link: str | None = Field(default=None, description="Enlace de pago")
    qr_image_url: str | None = Field(default=None, description="URL de imagen QR")
    is_active: bool | None = Field(default=None, description="Activar o desactivar")
