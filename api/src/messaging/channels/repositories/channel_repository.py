from sqlalchemy import select

from core.base.repository_base import RepositoryBase
from messaging.channels.enums.channel_enums import ChannelName
from messaging.channels.models.channel_model import ChannelModel


class ChannelRepository(RepositoryBase[ChannelModel]):
    model_class = ChannelModel

    async def get_by_name(self, name: ChannelName) -> ChannelModel | None:
        result = await self.session.execute(
            select(ChannelModel).where(ChannelModel.name == name)
        )
        return result.scalar_one_or_none()
