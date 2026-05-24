import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.soft_delete_repository_base import SoftDeleteRepositoryBase
from portfolios.models.portfolio_user_access_model import PortfolioUserAccessModel


class PortfolioUserAccessRepository(SoftDeleteRepositoryBase[PortfolioUserAccessModel]):
    model_class = PortfolioUserAccessModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_user_and_org(
        self, user_id: int, organization_id: uuid.UUID
    ) -> list[PortfolioUserAccessModel]:
        result = await self.session.execute(
            select(PortfolioUserAccessModel).where(
                PortfolioUserAccessModel.user_id == user_id,
                PortfolioUserAccessModel.organization_id == organization_id,
                PortfolioUserAccessModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_active_by_user_and_org(
        self, user_id: int, organization_id: uuid.UUID
    ) -> list[PortfolioUserAccessModel]:
        result = await self.session.execute(
            select(PortfolioUserAccessModel).where(
                PortfolioUserAccessModel.user_id == user_id,
                PortfolioUserAccessModel.organization_id == organization_id,
                PortfolioUserAccessModel.is_active.is_(True),
                PortfolioUserAccessModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_by_portfolio_id(
        self, portfolio_id: uuid.UUID
    ) -> list[PortfolioUserAccessModel]:
        result = await self.session.execute(
            select(PortfolioUserAccessModel).where(
                PortfolioUserAccessModel.portfolio_id == portfolio_id,
                PortfolioUserAccessModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_by_user_and_portfolio(
        self,
        user_id: int,
        portfolio_id: uuid.UUID,
        organization_id: uuid.UUID | None = None,
    ) -> PortfolioUserAccessModel | None:
        conditions = [
            PortfolioUserAccessModel.user_id == user_id,
            PortfolioUserAccessModel.portfolio_id == portfolio_id,
            PortfolioUserAccessModel.deleted_at.is_(None),
        ]
        if organization_id is not None:
            conditions.append(PortfolioUserAccessModel.organization_id == organization_id)

        result = await self.session.execute(
            select(PortfolioUserAccessModel).where(*conditions)
        )
        return result.scalars().first()

    async def check_active_access(
        self,
        user_id: int,
        portfolio_id: uuid.UUID,
        organization_id: uuid.UUID | None = None,
    ) -> bool:
        record = await self.get_by_user_and_portfolio(user_id, portfolio_id, organization_id)
        return record is not None and record.is_active
