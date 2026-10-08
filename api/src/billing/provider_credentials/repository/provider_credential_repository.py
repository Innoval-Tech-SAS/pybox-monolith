"""Acceso a datos de las credenciales de pasarela de facturación de la plataforma."""

from billing.provider_credentials.enums.provider_credential_enums import (
    PlatformGatewayProvider,
)
from billing.provider_credentials.models.provider_credential_model import (
    PlatformGatewayCredentialModel,
)
from core.base.credential_repository_mixin import CountryScopedCredentialRepositoryMixin
from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase


class PlatformGatewayCredentialRepository(
    CountryScopedCredentialRepositoryMixin[
        PlatformGatewayCredentialModel, PlatformGatewayProvider
    ],
    SoftDeleteRepositoryBase[PlatformGatewayCredentialModel],
):
    model_class = PlatformGatewayCredentialModel
