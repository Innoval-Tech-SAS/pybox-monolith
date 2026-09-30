"""Dependencias de FastAPI para inyectar el PortfolioService con sus repositories."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from messaging.campaigns.repository.campaign_repository import CampaignRepository
from messaging.contacts.repository.contact_repository import ContactRepository
from receivables.credits.repository.credit_repository import CreditRepository
from receivables.portfolios.repository.portfolio_daily_counter_config_repository import (  # pylint: disable=line-too-long
    PortfolioDailyCounterConfigRepository,
)
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository
from receivables.portfolios.repository.portfolio_user_access_repository import (
    PortfolioUserAccessRepository,
)
from receivables.portfolios.services.installment_csv_service import (
    InstallmentCsvService,
)
from receivables.portfolios.services.portfolio_csv_service import PortfolioCsvService
from receivables.portfolios.services.portfolio_service import PortfolioService
from receivables.portfolios.services.portfolio_user_access_service import (
    PortfolioUserAccessService,
)


def get_portfolio_csv_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> PortfolioCsvService:
    return PortfolioCsvService(session)


def get_installment_csv_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> InstallmentCsvService:
    return InstallmentCsvService(session)


def get_portfolio_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> PortfolioService:
    return PortfolioService(
        PortfolioRepository(session),
        PortfolioDailyCounterConfigRepository(session),
        CreditRepository(session),
        CampaignRepository(session),
        ContactRepository(session),
        PortfolioUserAccessRepository(session),
    )


def get_portfolio_user_access_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> PortfolioUserAccessService:
    return PortfolioUserAccessService(session)


PortfolioCsvServiceDep = Annotated[
    PortfolioCsvService, Depends(get_portfolio_csv_service)
]
InstallmentCsvServiceDep = Annotated[
    InstallmentCsvService, Depends(get_installment_csv_service)
]
PortfolioServiceDep = Annotated[PortfolioService, Depends(get_portfolio_service)]
PortfolioUserAccessServiceDep = Annotated[
    PortfolioUserAccessService, Depends(get_portfolio_user_access_service)
]
