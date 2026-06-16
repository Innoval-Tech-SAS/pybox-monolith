from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from receivables.contact_methods.repository.contact_method_repository import ContactMethodRepository
from receivables.credits.repository.credit_repository import CreditRepository
from core.database.database import get_main_session
from receivables.debtors.repository.address_repository import AddressRepository
from receivables.debtors.repository.debtor_repository import DebtorRepository
from receivables.debtors.services.debtor_service import DebtorService
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository


def get_debtor_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> DebtorService:
    return DebtorService(
        session=session,
        debtor_repo=DebtorRepository(session),
        address_repo=AddressRepository(session),
        contact_repo=ContactMethodRepository(session),
        portfolio_repo=PortfolioRepository(session),
        credit_repo=CreditRepository(session),
    )


DebtorServiceDep = Annotated[DebtorService, Depends(get_debtor_service)]
