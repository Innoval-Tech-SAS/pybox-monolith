from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from messaging.campaigns.repositories.campaign_repositories import CampaignRepository
from messaging.campaigns.repositories.campaign_time_repository import CampaignTimeRepository
from messaging.campaigns.services.campaign_service import CampaignService
from core.database.database import get_main_session


def get_campaign_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> CampaignService:
    return CampaignService(CampaignRepository(session), CampaignTimeRepository(session))


CampaignServiceDep = Annotated[CampaignService, Depends(get_campaign_service)]
