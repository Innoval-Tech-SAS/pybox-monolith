"""Tests de `ChannelService` (CRUD de canales de envío, ver channel_service.py).
Riesgo real: crear un canal con un `name` ya existente debe rechazarse con 409 en vez
de violar la constraint `unique` de BD, y todo lo que pasa por `get_by_id` (incluido
`update`/`delete`) debe dar 404 antes de tocar el repo de nuevo.

Unitario puro: `ChannelRepository` va mockeado.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from messaging.channels.enums.channel_enums import ChannelName, Currency
from messaging.channels.schemas.channel_schemas import (
    ChannelCreateRequest,
    ChannelUpdateRequest,
)
from messaging.channels.services.channel_service import ChannelService


def build_service():
    repo = MagicMock()
    return ChannelService(repo), repo


class TestGetByIdNotFound:
    async def test_missing_channel_raises_404(self):
        service, repo = build_service()
        repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_by_id(uuid.uuid4())

        assert exc_info.value.status_code == 404

    async def test_existing_channel_is_returned(self):
        service, repo = build_service()
        channel = MagicMock()
        repo.get_by_id = AsyncMock(return_value=channel)

        result = await service.get_by_id(uuid.uuid4())

        assert result is channel


class TestCreate:
    async def test_duplicate_name_raises_409_without_calling_add(self):
        service, repo = build_service()
        repo.get_by_name = AsyncMock(return_value=MagicMock())

        data = ChannelCreateRequest(
            name=ChannelName.SMS, label="SMS", unit_price="0.25", description="desc"
        )
        with pytest.raises(HTTPException) as exc_info:
            await service.create(data)

        assert exc_info.value.status_code == 409
        repo.add.assert_not_called()

    async def test_new_channel_is_created_with_provided_fields(self):
        service, repo = build_service()
        repo.get_by_name = AsyncMock(return_value=None)
        repo.add = AsyncMock(side_effect=lambda c: c)

        data = ChannelCreateRequest(
            name=ChannelName.SMS,
            label="SMS",
            currency=Currency.USD,
            unit_price="0.25",
            description="desc",
        )
        result = await service.create(data)

        assert result.name == ChannelName.SMS
        assert result.label == "SMS"
        assert result.currency == Currency.USD
        repo.add.assert_awaited_once()


class TestUpdate:
    async def test_partial_update_only_overwrites_provided_fields(self):
        service, repo = build_service()
        existing = MagicMock(label="Antigua", unit_price="0.25", description="vieja")
        repo.get_by_id = AsyncMock(return_value=existing)
        repo.update = AsyncMock(side_effect=lambda c: c)

        data = ChannelUpdateRequest(label="Nueva etiqueta")
        result = await service.update(uuid.uuid4(), data)

        assert result.label == "Nueva etiqueta"
        assert result.unit_price == "0.25"

    async def test_update_of_missing_channel_raises_404(self):
        service, repo = build_service()
        repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.update(uuid.uuid4(), ChannelUpdateRequest(label="x"))

        assert exc_info.value.status_code == 404


class TestDelete:
    async def test_delete_looks_up_before_deleting(self):
        service, repo = build_service()
        existing = MagicMock()
        repo.get_by_id = AsyncMock(return_value=existing)
        repo.delete = AsyncMock()

        await service.delete(uuid.uuid4())

        repo.delete.assert_awaited_once_with(existing)

    async def test_delete_of_missing_channel_raises_404(self):
        service, repo = build_service()
        repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.delete(uuid.uuid4())

        assert exc_info.value.status_code == 404


class TestListAll:
    async def test_returns_repo_result_as_is(self):
        service, repo = build_service()
        channels = [MagicMock(), MagicMock()]
        repo.get_all = AsyncMock(return_value=channels)

        result = await service.list_all()

        assert result == channels
