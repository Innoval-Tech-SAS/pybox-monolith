import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.soft_delete_repository_base import SoftDeleteRepositoryBase
from portfolios.models.portfolio_model import PortfolioModel


class PortfolioRepository(SoftDeleteRepositoryBase[PortfolioModel]):
    model_class = PortfolioModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_organization_id(self, organization_id: uuid.UUID) -> list[PortfolioModel]:
        result = await self.session.execute(
            select(PortfolioModel).where(
                PortfolioModel.organization_id == organization_id,
                PortfolioModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_active_by_organization_id(self, organization_id: uuid.UUID) -> list[PortfolioModel]:
        result = await self.session.execute(
            select(PortfolioModel).where(
                PortfolioModel.organization_id == organization_id,
                PortfolioModel.is_active.is_(True),
                PortfolioModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())
