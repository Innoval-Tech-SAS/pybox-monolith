from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.dashboard.services.dashboard_service import DashboardService
from core.database.database import get_main_session
from messaging.campaigns.repository.campaign_repository import CampaignRepository
from messaging.contacts.repository.contact_repository import ContactRepository
from receivables.credits.repository.credit_repository import CreditRepository
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository


def get_dashboard_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> DashboardService:
    return DashboardService(
        CreditRepository(session),
        PortfolioRepository(session),
        CampaignRepository(session),
        ContactRepository(session),
    )


DashboardServiceDep = Annotated[DashboardService, Depends(get_dashboard_service)]
