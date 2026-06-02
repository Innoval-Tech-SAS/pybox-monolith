import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.soft_delete_repository_base import SoftDeleteRepositoryBase
from campaigns.models.campaign_model import CampaignModel


class CampaignRepository(SoftDeleteRepositoryBase[CampaignModel]):
    model_class = CampaignModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def list_by_organization(self, organization_id: uuid.UUID) -> Sequence[CampaignModel]:
        result = await self.session.execute(
            select(CampaignModel).where(
                CampaignModel.organization_id == organization_id,
                CampaignModel.deleted_at.is_(None),
            ).order_by(CampaignModel.created_at.desc())
        )
        return result.scalars().all()

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
