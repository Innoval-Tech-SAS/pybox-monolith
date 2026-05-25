from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from base.repository_base import RepositoryBase
from notifications.models.notification_model import NotificationModel


class NotificationRepository(RepositoryBase[NotificationModel]):
    model_class = NotificationModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_user_id(self, user_id: int) -> Sequence[NotificationModel]:
        result = await self.session.execute(
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_id_and_user(self, notification_id: int, user_id: int) -> NotificationModel | None:
        result = await self.session.execute(
            select(NotificationModel).where(
                NotificationModel.id == notification_id,
                NotificationModel.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def mark_all_read(self, user_id: int) -> None:
        await self.session.execute(
            update(NotificationModel)
            .where(
                NotificationModel.user_id == user_id,
                NotificationModel.is_read.is_(False),
            )
            .values(is_read=True)
        )
        await self.session.flush()
