"""Acceso a datos de las credenciales de proveedor de mensajería."""

from sqlalchemy import select

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.provider_credentials.enums.provider_credential_enums import (
    MessagingCredentialProvider,
)
from messaging.provider_credentials.models.provider_credential_model import (
    MessagingProviderCredentialModel,
)


class MessagingProviderCredentialRepository(
    SoftDeleteRepositoryBase[MessagingProviderCredentialModel]
):
    model_class = MessagingProviderCredentialModel

    async def get(
        self, country_code: str | None, provider: MessagingCredentialProvider
    ) -> MessagingProviderCredentialModel | None:
        stmt = select(MessagingProviderCredentialModel).where(
            MessagingProviderCredentialModel.provider == provider,
            (
                MessagingProviderCredentialModel.country_code == country_code
                if country_code is not None
                else MessagingProviderCredentialModel.country_code.is_(None)
            ),
            MessagingProviderCredentialModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def resolve(
        self, country_code: str | None, provider: MessagingCredentialProvider
    ) -> MessagingProviderCredentialModel | None:
        """Credencial específica del país; si no existe, cae a la global (país NULL)."""
        if country_code is not None:
            specific = await self.get(country_code, provider)
            if specific is not None:
                return specific
        return await self.get(None, provider)

    async def get_by_lookup_key(
        self, provider: MessagingCredentialProvider, lookup_key: str
    ) -> MessagingProviderCredentialModel | None:
        result = await self.session.execute(
            select(MessagingProviderCredentialModel).where(
                MessagingProviderCredentialModel.provider == provider,
                MessagingProviderCredentialModel.lookup_key == lookup_key,
                MessagingProviderCredentialModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[MessagingProviderCredentialModel]:
        result = await self.session.execute(
            select(MessagingProviderCredentialModel).where(
                MessagingProviderCredentialModel.deleted_at.is_(None)
            )
        )
        return list(result.scalars().all())
