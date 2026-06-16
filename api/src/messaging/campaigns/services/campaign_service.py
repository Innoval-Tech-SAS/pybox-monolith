import uuid
from typing import Sequence

from fastapi import HTTPException, status

from messaging.campaigns.models.campaign_model import CampaignModel
from messaging.campaigns.repositories.campaign_repositories import CampaignRepository
from messaging.campaigns.schemas.campaign_schemas import CampaignCreateRequest, CampaignUpdateRequest


class CampaignService:

    def __init__(self, campaign_repo: CampaignRepository) -> None:
        self._repo = campaign_repo

    async def list_by_org(self, organization_id: uuid.UUID) -> Sequence[CampaignModel]:
        return await self._repo.list_by_organization(organization_id)

    async def get_by_id(self, campaign_id: uuid.UUID, organization_id: uuid.UUID) -> CampaignModel:
        campaign = await self._repo.get_by_id_and_org(campaign_id, organization_id)
        if campaign is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Campaña no encontrada")
        return campaign

    async def create(
        self, organization_id: uuid.UUID, data: CampaignCreateRequest
    ) -> CampaignModel:
        campaign = CampaignModel(
            organization_id=organization_id,
            name=data.name,
            message=data.message,
            subject=data.subject,
            channel=data.channel,
            description=data.description,
            status=data.status,
            total_recipients=data.total_recipients,
            scheduled_at=data.scheduled_at,
            timezone=data.timezone,
            fallback=data.fallback,
        )
        return await self._repo.add(campaign)

    async def update(
        self,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID,
        data: CampaignUpdateRequest,
    ) -> CampaignModel:
        campaign = await self.get_by_id(campaign_id, organization_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(campaign, key, value)
        return await self._repo.update(campaign)

    async def delete(self, campaign_id: uuid.UUID, organization_id: uuid.UUID) -> None:
        campaign = await self.get_by_id(campaign_id, organization_id)
        await self._repo.delete(campaign)
