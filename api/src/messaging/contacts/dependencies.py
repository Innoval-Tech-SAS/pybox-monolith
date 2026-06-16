from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from messaging.contacts.repositories.contact_repository import ContactRepository
from messaging.contacts.services.contact_service import ContactService


def get_contact_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> ContactService:
    return ContactService(repo=ContactRepository(session))


ContactServiceDep = Annotated[ContactService, Depends(get_contact_service)]
