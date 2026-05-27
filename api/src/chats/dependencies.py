from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from chats.repository.chat_repository import ChatRepository
from chats.repository.message_repository import MessageRepository
from chats.services.chat_service import ChatService
from database.database import get_main_session
from users.repository.user_repository import UserRepository


def get_chat_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> ChatService:
    return ChatService(
        chat_repo=ChatRepository(session),
        msg_repo=MessageRepository(session),
        user_repo=UserRepository(session),
    )


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
