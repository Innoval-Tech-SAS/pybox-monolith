import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.campaigns.enums.campaign_enums import CampaignStatus
from messaging.campaigns.models.campaign_model import CampaignModel
from receivables.portfolios.models.portfolio_model import PortfolioModel

_MANUAL_DESCRIPTION = "__manual__"


class CampaignRepository(SoftDeleteRepositoryBase[CampaignModel]):
    model_class = CampaignModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def list_by_portfolio(
        self,
        portfolio_id: uuid.UUID,
        page: int,
        page_size: int,
        search: str | None = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> tuple[list[CampaignModel], int]:
        query = select(CampaignModel).where(
            CampaignModel.portfolio_id == portfolio_id,
            CampaignModel.deleted_at.is_(None),
        )

        if search:
            query = query.where(CampaignModel.name.ilike(f"%{search}%"))

        _sort_cols = {
            "name": CampaignModel.name,
            "status": CampaignModel.status,
        }
        sort_col = _sort_cols.get(sort_by, CampaignModel.name)
        query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())

        total: int = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        ) or 0

        result = await self.session.execute(
            query.offset((page - 1) * page_size).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_by_id_and_portfolio(
        self, campaign_id: uuid.UUID, portfolio_id: uuid.UUID
    ) -> CampaignModel | None:
        result = await self.session.execute(
            select(CampaignModel).where(
                CampaignModel.id == campaign_id,
                CampaignModel.portfolio_id == portfolio_id,
                CampaignModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_by_organization_id(self, organization_id: uuid.UUID) -> list[CampaignModel]:
        result = await self.session.execute(
            select(CampaignModel)
            .join(PortfolioModel, PortfolioModel.id == CampaignModel.portfolio_id)
            .where(
                PortfolioModel.organization_id == organization_id,
                PortfolioModel.deleted_at.is_(None),
                CampaignModel.deleted_at.is_(None),
            )
            .order_by(CampaignModel.name)
        )
        return list(result.scalars().all())

    async def get_or_create_manual(
        self,
        portfolio_id: uuid.UUID,
        channel_id: uuid.UUID,
        channel_label: str,
    ) -> CampaignModel:
        result = await self.session.execute(
            select(CampaignModel).where(
                CampaignModel.portfolio_id == portfolio_id,
                CampaignModel.channel_id == channel_id,
                CampaignModel.description == _MANUAL_DESCRIPTION,
                CampaignModel.deleted_at.is_(None),
            )
        )
        campaign = result.scalar_one_or_none()
        if campaign is None:
            campaign = CampaignModel(
                portfolio_id=portfolio_id,
                channel_id=channel_id,
                name=f"Envío Manual — {channel_label}",
                description=_MANUAL_DESCRIPTION,
                message="",
                status=CampaignStatus.DRAFT,
            )
            await self.add(campaign)
        return campaign

    async def get_by_id_and_organization_id(
        self, campaign_id: uuid.UUID, organization_id: uuid.UUID
    ) -> CampaignModel | None:
        result = await self.session.execute(
            select(CampaignModel)
            .join(PortfolioModel, PortfolioModel.id == CampaignModel.portfolio_id)
            .where(
                CampaignModel.id == campaign_id,
                PortfolioModel.organization_id == organization_id,
                PortfolioModel.deleted_at.is_(None),
                CampaignModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()
