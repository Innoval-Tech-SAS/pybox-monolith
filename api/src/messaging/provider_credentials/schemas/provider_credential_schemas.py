import uuid
from datetime import datetime

from pydantic import Field

from core.base.schema_base import BaseSchema
from messaging.provider_credentials.enums.provider_credential_enums import MessagingCredentialProvider


class MessagingProviderCredentialUpsert(BaseSchema):
    country_code: str | None = Field(
        default=None,
        description="Código ISO del país; null = credencial global (todos los países)",
    )
    provider: MessagingCredentialProvider = Field(description="Proveedor de mensajería")
    secrets: dict[str, str] = Field(
        default_factory=dict,
        description="Valores secretos en claro (se cifran al guardar). Vacío = conservar los existentes. Enviar un valor rota ese secreto.",
    )
    public_config: dict[str, str] = Field(
        default_factory=dict,
        description="Valores NO secretos (sender, waba_id, sender_name)",
    )
    lookup_key: str | None = Field(
        default=None,
        description="Identificador del proveedor para resolver por igualdad",
    )
    is_active: bool = Field(default=True, description="Si la credencial está activa")


class MessagingProviderCredentialResponse(BaseSchema):
    """Salida de administración. NUNCA expone los valores secretos descifrados: solo
    lista los nombres de los secretos configurados (`secret_keys`)."""

    id: uuid.UUID
    country_code: str | None
    provider: MessagingCredentialProvider
    public_config: dict[str, str]
    secret_keys: list[str] = Field(
        description="Nombres de los secretos configurados (sin valores)"
    )
    lookup_key: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None
