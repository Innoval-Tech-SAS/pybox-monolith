from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from messaging.contacts.repository.contact_repository import ContactRepository
from messaging.contacts.services.contact_service import ContactService
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository


def get_contact_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> ContactService:
    return ContactService(
        repo=ContactRepository(session), portfolio_repo=PortfolioRepository(session)
    )


ContactServiceDep = Annotated[ContactService, Depends(get_contact_service)]
