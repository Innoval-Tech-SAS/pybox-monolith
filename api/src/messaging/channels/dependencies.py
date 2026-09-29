from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from messaging.channels.repository.channel_repository import ChannelRepository
from messaging.channels.services.channel_service import ChannelService


def get_channel_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> ChannelService:
    return ChannelService(repo=ChannelRepository(session))


ChannelServiceDep = Annotated[ChannelService, Depends(get_channel_service)]
