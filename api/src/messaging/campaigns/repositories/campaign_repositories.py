import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.campaigns.models.campaign_model import CampaignModel


class CampaignRepository(SoftDeleteRepositoryBase[CampaignModel]):
    model_class = CampaignModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def list_by_organization(
        self,
        organization_id: uuid.UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[CampaignModel], int]:
        query = select(CampaignModel).where(
            CampaignModel.organization_id == organization_id,
            CampaignModel.deleted_at.is_(None),
        )

        total: int = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        ) or 0

        result = await self.session.execute(
            query.order_by(CampaignModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_by_id_and_org(
        self, campaign_id: uuid.UUID, organization_id: uuid.UUID
    ) -> CampaignModel | None:
        result = await self.session.execute(
            select(CampaignModel).where(
                CampaignModel.id == campaign_id,
                CampaignModel.organization_id == organization_id,
                CampaignModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()
