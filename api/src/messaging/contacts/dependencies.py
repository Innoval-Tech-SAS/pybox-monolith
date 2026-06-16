from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from messaging.contacts.services.contact_service import ContactService
from core.database.database import get_main_session


def get_contact_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> ContactService:
    return ContactService(session)


ContactServiceDep = Annotated[ContactService, Depends(get_contact_service)]
