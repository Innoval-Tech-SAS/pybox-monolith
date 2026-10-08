"""Acceso a datos de las credenciales de proveedor de mensajería."""

from core.base.credential_repository_mixin import CountryScopedCredentialRepositoryMixin
from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.provider_credentials.enums.provider_credential_enums import (
    MessagingCredentialProvider,
)
from messaging.provider_credentials.models.provider_credential_model import (
    MessagingProviderCredentialModel,
)


class MessagingProviderCredentialRepository(
    CountryScopedCredentialRepositoryMixin[
        MessagingProviderCredentialModel, MessagingCredentialProvider
    ],
    SoftDeleteRepositoryBase[MessagingProviderCredentialModel],
):
    model_class = MessagingProviderCredentialModel
