"""Acceso a datos de los resultados agregados de ejecución de campaña."""

import uuid
from datetime import datetime, timezone

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.campaigns.models.campaign_result_model import CampaignResultModel


class CampaignResultRepository(SoftDeleteRepositoryBase[CampaignResultModel]):
    model_class = CampaignResultModel

    async def create(
        self,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID,
        campaign_time_id: uuid.UUID | None,
        total_sent: int,
        success_count: int,
        failure_count: int,
        unique_customers: int,
        sending_id: str | None = None,
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
            sending_id=sending_id,
        )
        return await self.add(result)

    async def soft_delete_by_organization(
        self, organization_id: uuid.UUID, deleted_at: datetime
    ) -> None:
        """Baja en cascada de los resultados de campañas de la
        organización con el sello de la organización."""
        await self.soft_delete_where(
            CampaignResultModel.organization_id == organization_id,
            deleted_at=deleted_at,
        )

    async def restore_by_organization(
        self, organization_id: uuid.UUID, deleted_at: datetime
    ) -> None:
        """Inverso de ``soft_delete_by_organization``: solo lo que cayó
        con la organización."""
        await self.restore_where(
            CampaignResultModel.organization_id == organization_id,
            deleted_at=deleted_at,
        )
