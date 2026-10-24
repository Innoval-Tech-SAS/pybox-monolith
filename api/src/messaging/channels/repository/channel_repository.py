"""Acceso a datos de los canales de mensajería."""

from sqlalchemy import select

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.channels.enums.channel_enums import ChannelName
from messaging.channels.models.channel_model import ChannelModel


class ChannelRepository(SoftDeleteRepositoryBase[ChannelModel]):
    model_class = ChannelModel

    async def get_by_name(self, name: ChannelName) -> ChannelModel | None:
        result = await self.session.execute(
            select(ChannelModel).where(
                ChannelModel.name == name, ChannelModel.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()
