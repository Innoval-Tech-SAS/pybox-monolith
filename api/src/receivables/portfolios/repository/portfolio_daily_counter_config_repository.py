import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.portfolios.models.portfolio_daily_counter_config_model import PortfolioDailyCounterConfigModel


class PortfolioDailyCounterConfigRepository(SoftDeleteRepositoryBase[PortfolioDailyCounterConfigModel]):
    model_class = PortfolioDailyCounterConfigModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_portfolio_id(
        self, portfolio_id: uuid.UUID
    ) -> PortfolioDailyCounterConfigModel | None:
        result = await self.session.execute(
            select(PortfolioDailyCounterConfigModel).where(
                PortfolioDailyCounterConfigModel.portfolio_id == portfolio_id,
                PortfolioDailyCounterConfigModel.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    async def get_enabled(self) -> list[PortfolioDailyCounterConfigModel]:
        result = await self.session.execute(
            select(PortfolioDailyCounterConfigModel).where(
                PortfolioDailyCounterConfigModel.enabled.is_(True),
                PortfolioDailyCounterConfigModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())
