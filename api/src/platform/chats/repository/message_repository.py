from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.repository_base import RepositoryBase
from platform.chats.models.message_model import MessageModel
from platform.chats.models.message_status_model import MessageStatusModel


class MessageRepository(RepositoryBase[MessageModel]):
    model_class = MessageModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_chat_messages(
        self, chat_id: str, before_ts: datetime | None, limit: int
    ) -> list[MessageModel]:
        query = (
            select(MessageModel)
            .where(MessageModel.chat_id == chat_id)
            .order_by(MessageModel.created_at.desc())
            .limit(limit)
        )
        if before_ts:
            query = query.where(MessageModel.created_at < before_ts)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_last_message(self, chat_id: str) -> MessageModel | None:
        result = await self.session.execute(
            select(MessageModel)
            .where(MessageModel.chat_id == chat_id)
            .order_by(MessageModel.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def add_statuses(self, statuses: list[MessageStatusModel]) -> None:
        self.session.add_all(statuses)
        await self.session.flush()

    async def mark_read(self, message_id: str, user_id: int, now: datetime) -> None:
        await self.session.execute(
            update(MessageStatusModel)
            .where(
                MessageStatusModel.message_id == message_id,
                MessageStatusModel.user_id == user_id,
            )
            .values(read_at=now)
        )
        await self.session.flush()

    async def get_unread_count(self, chat_id: str, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count(MessageModel.id))
            .join(MessageStatusModel, MessageStatusModel.message_id == MessageModel.id)
            .where(
                MessageModel.chat_id == chat_id,
                MessageStatusModel.user_id == user_id,
                MessageStatusModel.read_at.is_(None),
                MessageModel.sender_id != user_id,
            )
        )
        return result.scalar() or 0

    async def get_unread_message_ids(self, chat_id: str, user_id: int) -> list[str]:
        result = await self.session.execute(
            select(MessageStatusModel.message_id)
            .join(MessageModel, MessageModel.id == MessageStatusModel.message_id)
            .where(
                MessageModel.chat_id == chat_id,
                MessageStatusModel.user_id == user_id,
                MessageStatusModel.read_at.is_(None),
                MessageModel.sender_id != user_id,
            )
        )
        return list(result.scalars().all())

    async def mark_all_read(self, chat_id: str, user_id: int, now: datetime) -> None:
        await self.session.execute(
            update(MessageStatusModel)
            .where(
                MessageStatusModel.user_id == user_id,
                MessageStatusModel.read_at.is_(None),
                MessageStatusModel.message_id.in_(
                    select(MessageModel.id).where(
                        MessageModel.chat_id == chat_id,
                        MessageModel.sender_id != user_id,
                    )
                ),
            )
            .values(read_at=now)
        )
        await self.session.flush()

    async def get_statuses_for_messages(
        self, message_ids: list[str]
    ) -> dict[str, list[MessageStatusModel]]:
        if not message_ids:
            return {}
        result = await self.session.execute(
            select(MessageStatusModel).where(
                MessageStatusModel.message_id.in_(message_ids)
            )
        )
        out: dict[str, list[MessageStatusModel]] = {}
        for s in result.scalars().all():
            out.setdefault(s.message_id, []).append(s)
        return out
