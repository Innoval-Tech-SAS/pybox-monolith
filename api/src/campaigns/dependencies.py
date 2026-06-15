from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from campaigns.repositories.campaign_repositories import CampaignRepository
from campaigns.services.campaign_service import CampaignService
from database.database import get_main_session


def get_campaign_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> CampaignService:
    return CampaignService(CampaignRepository(session))


CampaignServiceDep = Annotated[CampaignService, Depends(get_campaign_service)]
