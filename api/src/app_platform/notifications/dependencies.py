"""Dependencia de FastAPI para inyectar el NotificationService."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.notifications.services.notification_service import NotificationService
from core.database.database import get_main_session


def get_notification_service(
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> NotificationService:
    return NotificationService(db)


NotificationServiceDep = Annotated[
    NotificationService, Depends(get_notification_service)
]
