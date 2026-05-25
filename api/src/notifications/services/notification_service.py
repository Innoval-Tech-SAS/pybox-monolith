from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from notifications.models.notification_model import NotificationModel
from notifications.repository.notification_repository import NotificationRepository
from notifications.schemas.notification_schemas import NotificationSchema
from sse.sse_emitter import sse_emitter


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = NotificationRepository(session)

    async def get_notifications(self, user_id: int) -> list[NotificationSchema]:
        items = await self._repo.get_by_user_id(user_id)
        return [NotificationSchema.model_validate(n) for n in items]

    async def get_notification(self, notification_id: int, user_id: int) -> NotificationSchema | None:
        n = await self._repo.get_by_id_and_user(notification_id, user_id)
        return NotificationSchema.model_validate(n) if n else None

    async def mark_all_read(self, user_id: int) -> None:
        await self._repo.mark_all_read(user_id)

    async def create_notification(
        self,
        user_id: int,
        title: str,
        body: str,
        category: str,
        notif_type: str = "info",
        link: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> NotificationSchema:
        notification = await self._repo.add(
            NotificationModel(
                user_id=user_id,
                title=title,
                body=body,
                category=category,
                notif_type=notif_type,
                link=link,
                details=details,
            )
        )
        schema = NotificationSchema.model_validate(notification)
        await sse_emitter.emit(user_id, "notification", schema.model_dump(mode="json", by_alias=True))
        return schema
