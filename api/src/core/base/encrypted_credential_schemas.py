"""Campos comunes de administración de una credencial cifrada de proveedor externo."""

import uuid
from datetime import datetime

from pydantic import Field

from core.base.schema_base import BaseSchema


class EncryptedCredentialUpsertBase(BaseSchema):
    """Campos de alta/edición comunes a `billing.provider_credentials` y
    `messaging.provider_credentials`. Cada schema concreto agrega su propio
    `country_code` (mismo nombre en ambos) y `provider` (enum propio del dominio)."""

    secrets: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Valores secretos en claro (se cifran al guardar). Vacío = conservar "
            "los existentes. Enviar un valor rota ese secreto."
        ),
    )
    public_config: dict[str, str] = Field(
        default_factory=dict,
        description="Valores NO secretos de configuración del proveedor",
    )
    lookup_key: str | None = Field(
        default=None,
        description="Identificador del proveedor para resolver por igualdad",
    )
    is_active: bool = Field(default=True, description="Si la credencial está activa")


class EncryptedCredentialResponseBase(BaseSchema):
    """Salida de administración común. NUNCA expone los valores secretos
    descifrados: solo lista los nombres de los secretos configurados
    (`secret_keys`)."""

    id: uuid.UUID
    public_config: dict[str, str]
    secret_keys: list[str] = Field(
        description="Nombres de los secretos configurados (sin valores)"
    )
    lookup_key: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None
