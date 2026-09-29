"""Alta, edición y consulta de canales de mensajería."""

import uuid
from typing import Sequence

from fastapi import HTTPException, status

from messaging.channels.models.channel_model import ChannelModel
from messaging.channels.repository.channel_repository import ChannelRepository
from messaging.channels.schemas.channel_schemas import (
    ChannelCreateRequest,
    ChannelUpdateRequest,
)


class ChannelService:
    def __init__(self, repo: ChannelRepository) -> None:
        self._repo = repo

    async def list_all(self) -> Sequence[ChannelModel]:
        return await self._repo.get_all()

    async def get_by_id(self, channel_id: uuid.UUID) -> ChannelModel:
        channel = await self._repo.get_by_id(channel_id)
        if channel is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Canal no encontrado")
        return channel

    async def create(self, data: ChannelCreateRequest) -> ChannelModel:
        existing = await self._repo.get_by_name(data.name)
        if existing is not None:
            raise HTTPException(
                status.HTTP_409_CONFLICT, f"El canal '{data.name}' ya existe"
            )
        channel = ChannelModel(
            name=data.name,
            label=data.label,
            currency=data.currency,
            unit_price=data.unit_price,
            description=data.description,
        )
        return await self._repo.add(channel)

    async def update(
        self, channel_id: uuid.UUID, data: ChannelUpdateRequest
    ) -> ChannelModel:
        channel = await self.get_by_id(channel_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(channel, key, value)
        return await self._repo.update(channel)

    async def delete(self, channel_id: uuid.UUID) -> None:
        channel = await self.get_by_id(channel_id)
        await self._repo.delete(channel)

    async def restore(self, channel_id: uuid.UUID) -> ChannelModel:
        channel = await self._repo.get_by_id_including_deleted(channel_id)
        if channel is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Canal no encontrado")
        return await self._repo.restore(channel)
