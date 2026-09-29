import uuid

from pydantic import Field

from core.base.schema_base import BaseSchema


class WhatsAppOrgCredentialsRequest(BaseSchema):
    phone_number_id: str = Field(
        description="phone_number_id del número de WhatsApp de Meta"
    )
    display_name: str | None = Field(
        default=None, description="Nombre visible del número, opcional"
    )
    active: bool = Field(
        default=True, description="Si el número está activo para envíos"
    )


class WhatsAppOrgCredentialsResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID de la configuración")
    organization_id: uuid.UUID = Field(description="Organización dueña del número")
    phone_number_id: str = Field(description="phone_number_id de Meta")
    display_name: str | None = Field(
        default=None, description="Nombre visible del número"
    )
    active: bool = Field(description="Si el número está activo para envíos")
