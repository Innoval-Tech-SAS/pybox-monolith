from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_main_session
from portfolios.repository.portfolio_repository import PortfolioRepository
from portfolios.services.portfolio_csv_service import PortfolioCsvService
from portfolios.services.portfolio_service import PortfolioService
from portfolios.services.portfolio_user_access_service import PortfolioUserAccessService


def get_portfolio_csv_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> PortfolioCsvService:
    return PortfolioCsvService(session)


def get_portfolio_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> PortfolioService:
    return PortfolioService(session, PortfolioRepository(session))


def get_portfolio_user_access_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> PortfolioUserAccessService:
    return PortfolioUserAccessService(session)


PortfolioCsvServiceDep = Annotated[PortfolioCsvService, Depends(get_portfolio_csv_service)]
PortfolioServiceDep = Annotated[PortfolioService, Depends(get_portfolio_service)]
PortfolioUserAccessServiceDep = Annotated[PortfolioUserAccessService, Depends(get_portfolio_user_access_service)]
