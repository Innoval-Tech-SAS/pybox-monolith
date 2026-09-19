from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_self
from identity.users.schemas.user_session_schema import UserSession
from receivables.judicial_notifications.services.judicial_notification_service import (
    JudicialNotificationService,
)


def get_judicial_notification_service(
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> JudicialNotificationService:
    return JudicialNotificationService(db)


def require_self_session(session: CurrentSession) -> UserSession:
    """Gate de scope SELF a nivel de ruta para el buzón del titular: rechaza en el borde
    a quien no sea el titular. La política pura vive en security_policies."""
    require_self(session)
    return session


JudicialNotificationServiceDep = Annotated[
    JudicialNotificationService, Depends(get_judicial_notification_service)
]
RequireSelf = Annotated[UserSession, Depends(require_self_session)]
