import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from core.base.repository_base import RepositoryBase
from messaging.campaigns.models.campaign_result_model import CampaignResultModel


class CampaignResultRepository(RepositoryBase[CampaignResultModel]):
    model_class = CampaignResultModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(
        self,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID,
        campaign_time_id: uuid.UUID | None,
        total_sent: int,
        success_count: int,
        failure_count: int,
        unique_customers: int,
    ) -> CampaignResultModel:
        result = CampaignResultModel(
            campaign_id=campaign_id,
            organization_id=organization_id,
            campaign_time_id=campaign_time_id,
            total_sent=total_sent,
            success_count=success_count,
            failure_count=failure_count,
            unique_customers=unique_customers,
            sent_at=datetime.now(timezone.utc),
        )
        return await self.add(result)
