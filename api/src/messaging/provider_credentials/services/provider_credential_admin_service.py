"""Gestión admin (alta/edición/borrado) de credenciales de proveedor de mensajería."""

from sqlalchemy.ext.asyncio import AsyncSession

from core.base.encrypted_credential_admin_service import (
    EncryptedCredentialAdminServiceBase,
)
from messaging.provider_credentials.models.provider_credential_model import (
    MessagingProviderCredentialModel,
)
from messaging.provider_credentials.repository.provider_credential_repository import (
    MessagingProviderCredentialRepository,
)
from messaging.provider_credentials.schemas.provider_credential_schemas import (
    MessagingProviderCredentialResponse,
    MessagingProviderCredentialUpsert,
)


class MessagingProviderCredentialAdminService(
    EncryptedCredentialAdminServiceBase[
        MessagingProviderCredentialModel,
        MessagingProviderCredentialUpsert,
        MessagingProviderCredentialResponse,
    ]
):
    """Administración de credenciales de mensajería (solo ADMIN GLOBAL). Cifra los
    secretos al escribir y NUNCA los devuelve descifrados."""

    model_class = MessagingProviderCredentialModel
    response_class = MessagingProviderCredentialResponse

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(MessagingProviderCredentialRepository(session))
