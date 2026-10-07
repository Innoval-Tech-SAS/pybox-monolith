"""Gestión admin (alta/edición/borrado) de credenciales de pasarela de la plataforma."""

from sqlalchemy.ext.asyncio import AsyncSession

from billing.provider_credentials.models.provider_credential_model import (
    PlatformGatewayCredentialModel,
)
from billing.provider_credentials.repository.provider_credential_repository import (
    PlatformGatewayCredentialRepository,
)
from billing.provider_credentials.schemas.provider_credential_schemas import (
    PlatformGatewayCredentialResponse,
    PlatformGatewayCredentialUpsert,
)
from core.base.encrypted_credential_admin_service import (
    EncryptedCredentialAdminServiceBase,
)


class PlatformGatewayCredentialAdminService(
    EncryptedCredentialAdminServiceBase[
        PlatformGatewayCredentialModel,
        PlatformGatewayCredentialUpsert,
        PlatformGatewayCredentialResponse,
    ]
):
    """Administración de credenciales de pasarela de la plataforma (solo ADMIN GLOBAL).
    Cifra los secretos al escribir y NUNCA los devuelve descifrados."""

    model_class = PlatformGatewayCredentialModel
    response_class = PlatformGatewayCredentialResponse

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(PlatformGatewayCredentialRepository(session))
