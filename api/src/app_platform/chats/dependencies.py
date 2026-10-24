"""Dependencia de FastAPI para inyectar el ChatService con sus repositories."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.chats.repository.chat_repository import ChatRepository
from app_platform.chats.repository.message_repository import MessageRepository
from app_platform.chats.services.chat_service import ChatService
from core.database.database import get_main_session
from identity.organizations.repository.organization_membership_repository import (
    OrganizationMembershipRepository,
)
from identity.users.repository.role_assignment_repository import (
    RoleAssignmentRepository,
)
from identity.users.repository.user_repository import UserRepository


def get_chat_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> ChatService:
    return ChatService(
        chat_repo=ChatRepository(session),
        msg_repo=MessageRepository(session),
        user_repo=UserRepository(session),
        org_membership_repo=OrganizationMembershipRepository(session),
        role_assignment_repo=RoleAssignmentRepository(session),
    )


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
