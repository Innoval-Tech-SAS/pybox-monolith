from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from app_platform.provider_credentials.enums.provider_credential_enums import CredentialProvider
from app_platform.provider_credentials.models.provider_credential_model import ProviderCredentialModel


class ProviderCredentialRepository(SoftDeleteRepositoryBase[ProviderCredentialModel]):
    model_class = ProviderCredentialModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get(
        self, country_code: str | None, provider: CredentialProvider
    ) -> ProviderCredentialModel | None:
        stmt = select(ProviderCredentialModel).where(
            ProviderCredentialModel.provider == provider,
            ProviderCredentialModel.country_code == country_code
            if country_code is not None
            else ProviderCredentialModel.country_code.is_(None),
            ProviderCredentialModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def resolve(
        self, country_code: str | None, provider: CredentialProvider
    ) -> ProviderCredentialModel | None:
        """Credencial específica del país; si no existe, cae a la global (país NULL)."""
        if country_code is not None:
            specific = await self.get(country_code, provider)
            if specific is not None:
                return specific
        return await self.get(None, provider)

    async def get_by_lookup_key(
        self, provider: CredentialProvider, lookup_key: str
    ) -> ProviderCredentialModel | None:
        result = await self.session.execute(
            select(ProviderCredentialModel).where(
                ProviderCredentialModel.provider == provider,
                ProviderCredentialModel.lookup_key == lookup_key,
                ProviderCredentialModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[ProviderCredentialModel]:
        result = await self.session.execute(
            select(ProviderCredentialModel).where(ProviderCredentialModel.deleted_at.is_(None))
        )
        return list(result.scalars().all())
