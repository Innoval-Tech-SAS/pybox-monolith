from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_self
from identity.users.schemas.user_session_schema import UserSession
from receivables.contact_methods.repository.contact_method_repository import ContactMethodRepository
from receivables.credits.repository.credit_repository import CreditRepository
from receivables.debtors.repository.address_repository import AddressRepository
from receivables.debtors.repository.debtor_document_repository import DebtorDocumentRepository
from receivables.debtors.repository.debtor_repository import DebtorRepository
from receivables.debtors.services.debtor_document_service import DebtorDocumentService
from receivables.debtors.services.debtor_identity_service import DebtorIdentityService
from receivables.debtors.services.debtor_service import DebtorService
from receivables.payments.repository.payment_repository import PaymentRepository
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
        payment_repo=PaymentRepository(session),
        document_repo=DebtorDocumentRepository(session),
    )


def get_debtor_document_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> DebtorDocumentService:
    return DebtorDocumentService(session)


def get_debtor_identity_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> DebtorIdentityService:
    return DebtorIdentityService(
        debtor_repo=DebtorRepository(session),
        contact_repo=ContactMethodRepository(session),
    )


def require_self_session(session: CurrentSession) -> UserSession:
    """Gate de scope SELF a nivel de ruta para el repositorio documental del titular:
    rechaza en el borde a quien no sea el titular. La política pura vive en
    security_policies."""
    require_self(session)
    return session


DebtorServiceDep = Annotated[DebtorService, Depends(get_debtor_service)]
DebtorDocumentServiceDep = Annotated[DebtorDocumentService, Depends(get_debtor_document_service)]
DebtorIdentityServiceDep = Annotated[DebtorIdentityService, Depends(get_debtor_identity_service)]
RequireSelf = Annotated[UserSession, Depends(require_self_session)]
