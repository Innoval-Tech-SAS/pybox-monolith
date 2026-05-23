from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_main_session
from portfolios.services.portfolio_csv_service import PortfolioCsvService


def get_portfolio_csv_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> PortfolioCsvService:
    return PortfolioCsvService(session)


PortfolioCsvServiceDep = Annotated[PortfolioCsvService, Depends(get_portfolio_csv_service)]
