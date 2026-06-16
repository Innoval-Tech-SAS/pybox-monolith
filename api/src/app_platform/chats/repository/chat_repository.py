import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.repository_base import RepositoryBase
from app_platform.chats.models.chat_member_model import ChatMemberModel
from app_platform.chats.models.chat_model import ChatModel


class ChatRepository(RepositoryBase[ChatModel]):
    model_class = ChatModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_dm_key(self, dm_key: str) -> ChatModel | None:
        result = await self.session.execute(
            select(ChatModel).where(ChatModel.dm_key == dm_key)
        )
        return result.scalars().first()

    async def get_user_chats(self, user_id: uuid.UUID) -> list[ChatModel]:
        result = await self.session.execute(
            select(ChatModel)
            .join(ChatMemberModel, ChatMemberModel.chat_id == ChatModel.id)
            .where(
                ChatMemberModel.user_id == user_id,
                ChatMemberModel.left_at.is_(None),
            )
            .order_by(ChatModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def add_member(self, member: ChatMemberModel) -> ChatMemberModel:
        self.session.add(member)
        await self.session.flush()
        await self.session.refresh(member)
        return member

    async def get_member(self, chat_id: uuid.UUID, user_id: uuid.UUID) -> ChatMemberModel | None:
        result = await self.session.execute(
            select(ChatMemberModel).where(
                ChatMemberModel.chat_id == chat_id,
                ChatMemberModel.user_id == user_id,
            )
        )
        return result.scalars().first()

    async def get_active_members(self, chat_id: uuid.UUID) -> list[ChatMemberModel]:
        result = await self.session.execute(
            select(ChatMemberModel).where(
                ChatMemberModel.chat_id == chat_id,
                ChatMemberModel.left_at.is_(None),
            )
        )
        return list(result.scalars().all())
