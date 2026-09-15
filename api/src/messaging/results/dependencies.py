from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from messaging.contacts.repository.contact_repository import ContactRepository
from messaging.results.services.webhook_service import WebhookService


def get_webhook_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> WebhookService:
    return WebhookService(ContactRepository(session))


WebhookServiceDep = Annotated[WebhookService, Depends(get_webhook_service)]
