import uuid
from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.repository_base import RepositoryBase
from messaging.campaigns.models.campaign_model import CampaignModel
from messaging.campaigns.models.campaign_time_model import CampaignTimeModel


class CampaignTimeRepository(RepositoryBase[CampaignTimeModel]):
    model_class = CampaignTimeModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_active_by_org(
        self, organization_id: uuid.UUID
    ) -> Sequence[tuple[CampaignTimeModel, CampaignModel]]:
        stmt = (
            select(CampaignTimeModel, CampaignModel)
            .join(CampaignModel, CampaignTimeModel.campaign_id == CampaignModel.id)
            .where(
                CampaignTimeModel.organization_id == organization_id,
                CampaignTimeModel.is_active.is_(True),
                CampaignModel.deleted_at.is_(None),
            )
            .order_by(CampaignTimeModel.next_execution)
        )
        result = await self.session.execute(stmt)
        return [tuple(row) for row in result.all()]

    async def find_due_active(
        self, now: datetime, limit: int = 300, after_id: uuid.UUID | None = None
    ) -> Sequence[CampaignTimeModel]:
        stmt = (
            select(CampaignTimeModel)
            .where(
                CampaignTimeModel.is_active.is_(True),
                CampaignTimeModel.next_execution <= now,
            )
            .order_by(CampaignTimeModel.id)
            .limit(limit)
        )
        if after_id is not None:
            stmt = stmt.where(CampaignTimeModel.id > after_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_campaign(self, campaign_id: uuid.UUID) -> CampaignTimeModel | None:
        result = await self.session.execute(
            select(CampaignTimeModel).where(CampaignTimeModel.campaign_id == campaign_id)
        )
        return result.scalar_one_or_none()

    async def deactivate(self, ct: CampaignTimeModel) -> CampaignTimeModel:
        ct.is_active = False
        ct.next_execution = None
        return await self.update(ct)

    async def reschedule(self, ct: CampaignTimeModel, next_execution: datetime) -> CampaignTimeModel:
        ct.next_execution = next_execution
        return await self.update(ct)
