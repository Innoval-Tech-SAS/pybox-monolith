"""Dependencia de FastAPI para inyectar el StatementService con sus repositories."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from identity.organizations.repository.organization_repository import (
    OrganizationRepository,
)
from receivables.credits.repository.credit_repository import CreditRepository
from receivables.debtors.repository.debtor_repository import DebtorRepository
from receivables.payments.repository.payment_repository import PaymentRepository
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository
from receivables.statements.repository.statement_repository import StatementRepository
from receivables.statements.services.statement_service import StatementService


def get_statement_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> StatementService:
    return StatementService(
        session=session,
        statement_repo=StatementRepository(session),
        debtor_repo=DebtorRepository(session),
        portfolio_repo=PortfolioRepository(session),
        credit_repo=CreditRepository(session),
        payment_repo=PaymentRepository(session),
        organization_repo=OrganizationRepository(session),
    )


StatementServiceDep = Annotated[StatementService, Depends(get_statement_service)]
