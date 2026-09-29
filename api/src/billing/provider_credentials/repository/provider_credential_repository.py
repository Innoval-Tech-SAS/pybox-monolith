from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from billing.provider_credentials.enums.provider_credential_enums import PlatformGatewayProvider
from billing.provider_credentials.models.provider_credential_model import PlatformGatewayCredentialModel


class PlatformGatewayCredentialRepository(SoftDeleteRepositoryBase[PlatformGatewayCredentialModel]):
    model_class = PlatformGatewayCredentialModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get(
        self, country_code: str | None, provider: PlatformGatewayProvider
    ) -> PlatformGatewayCredentialModel | None:
        stmt = select(PlatformGatewayCredentialModel).where(
            PlatformGatewayCredentialModel.provider == provider,
            PlatformGatewayCredentialModel.country_code == country_code
            if country_code is not None
            else PlatformGatewayCredentialModel.country_code.is_(None),
            PlatformGatewayCredentialModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def resolve(
        self, country_code: str | None, provider: PlatformGatewayProvider
    ) -> PlatformGatewayCredentialModel | None:
        """Credencial específica del país; si no existe, cae a la global (país NULL)."""
        if country_code is not None:
            specific = await self.get(country_code, provider)
            if specific is not None:
                return specific
        return await self.get(None, provider)

    async def get_by_lookup_key(
        self, provider: PlatformGatewayProvider, lookup_key: str
    ) -> PlatformGatewayCredentialModel | None:
        result = await self.session.execute(
            select(PlatformGatewayCredentialModel).where(
                PlatformGatewayCredentialModel.provider == provider,
                PlatformGatewayCredentialModel.lookup_key == lookup_key,
                PlatformGatewayCredentialModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[PlatformGatewayCredentialModel]:
        result = await self.session.execute(
            select(PlatformGatewayCredentialModel).where(PlatformGatewayCredentialModel.deleted_at.is_(None))
        )
        return list(result.scalars().all())
