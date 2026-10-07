"""Schemas de credenciales de proveedor de mensajería."""

from pydantic import Field

from core.base.encrypted_credential_schemas import (
    EncryptedCredentialResponseBase,
    EncryptedCredentialUpsertBase,
)
from messaging.provider_credentials.enums.provider_credential_enums import (
    MessagingCredentialProvider,
)


class MessagingProviderCredentialUpsert(EncryptedCredentialUpsertBase):
    country_code: str | None = Field(
        default=None,
        description="Código ISO del país; null = credencial global (todos los países)",
    )
    provider: MessagingCredentialProvider = Field(description="Proveedor de mensajería")


class MessagingProviderCredentialResponse(EncryptedCredentialResponseBase):
    country_code: str | None
    provider: MessagingCredentialProvider
