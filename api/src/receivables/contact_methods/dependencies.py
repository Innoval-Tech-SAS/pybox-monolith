from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from receivables.contact_methods.repository.contact_method_repository import ContactMethodRepository
from receivables.contact_methods.services.self_service_contact_service import SelfServiceContactService
from receivables.debtors.repository.debtor_repository import DebtorRepository


def get_self_service_contact_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> SelfServiceContactService:
    return SelfServiceContactService(
        session=session,
        debtor_repo=DebtorRepository(session),
        contact_repo=ContactMethodRepository(session),
    )


SelfServiceContactServiceDep = Annotated[
    SelfServiceContactService, Depends(get_self_service_contact_service)
]
