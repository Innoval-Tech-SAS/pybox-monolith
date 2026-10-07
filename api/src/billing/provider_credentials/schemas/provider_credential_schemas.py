"""Schemas de credenciales de pasarela de facturación de la plataforma."""

from pydantic import Field

from billing.provider_credentials.enums.provider_credential_enums import (
    PlatformGatewayProvider,
)
from core.base.encrypted_credential_schemas import (
    EncryptedCredentialResponseBase,
    EncryptedCredentialUpsertBase,
)


class PlatformGatewayCredentialUpsert(EncryptedCredentialUpsertBase):
    country_code: str | None = Field(
        default=None,
        description=(
            "Código ISO del país; null = credencial global (todos los países)"
        ),
    )
    provider: PlatformGatewayProvider = Field(
        description="Pasarela con la que PYBOX cobra a sus organizaciones"
    )


class PlatformGatewayCredentialResponse(EncryptedCredentialResponseBase):
    country_code: str | None
    provider: PlatformGatewayProvider
