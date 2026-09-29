import uuid
from datetime import datetime

from pydantic import Field

from core.base.schema_base import BaseSchema
from receivables.payment_gateways.enums.payment_gateway_enums import (
    ReceivablesGatewayProvider,
)


class OrganizationGatewayCredentialCreateRequest(BaseSchema):
    provider: ReceivablesGatewayProvider = Field(
        description="Pasarela con la que esta organización cobra a sus deudores"
    )
    secrets: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Valores secretos en claro (se cifran al guardar): llaves "
            "privadas/de eventos/de integridad, según la pasarela"
        ),
    )
    public_config: dict[str, str] = Field(
        default_factory=dict,
        description="Valores NO secretos (p. ej. llave pública)",
    )
    lookup_key: str | None = Field(
        default=None,
        description=(
            "Identificador de comercio para resolver por igualdad en el "
            "webhook, si la pasarela lo soporta (ver skill wompi-gateway)"
        ),
    )
    is_active: bool = Field(default=True, description="Si la credencial está activa")


class OrganizationGatewayCredentialUpdateRequest(BaseSchema):
    secrets: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Vacío = conservar los existentes. Enviar un valor rota ese secreto."
        ),
    )
    public_config: dict[str, str] | None = Field(default=None)
    lookup_key: str | None = Field(default=None)
    is_active: bool | None = Field(default=None)


class OrganizationGatewayCredentialResponse(BaseSchema):
    """Salida de administración. NUNCA expone los valores secretos descifrados: solo
    lista los nombres de los secretos configurados (`secret_keys`)."""

    id: uuid.UUID
    organization_id: uuid.UUID
    provider: ReceivablesGatewayProvider
    public_config: dict[str, str]
    secret_keys: list[str] = Field(
        description="Nombres de los secretos configurados (sin valores)"
    )
    lookup_key: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None
