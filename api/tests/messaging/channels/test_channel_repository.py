"""Tests de `ChannelRepository.get_by_name` contra la base de datos real, mismo
patrón que `tests/receivables/test_credit_repository.py`. Los 5 canales ya vienen
sembrados por `seed_channels` (ver `_prepared_database` en conftest.py) -- no hace
falta crearlos, solo verificar que la búsqueda por nombre resuelve el correcto y que
un nombre sin canal devuelve `None` en vez de reventar.
"""

from sqlalchemy import delete

from messaging.channels.enums.channel_enums import ChannelName
from messaging.channels.models.channel_model import ChannelModel
from messaging.channels.repository.channel_repository import ChannelRepository


class TestGetByName:
    async def test_returns_the_seeded_channel_for_that_name(self, db_session):
        repo = ChannelRepository(db_session)

        channel = await repo.get_by_name(ChannelName.WHATSAPP)

        assert channel is not None
        assert channel.name == ChannelName.WHATSAPP

    async def test_returns_none_when_no_channel_has_that_name(self, db_session):
        repo = ChannelRepository(db_session)
        # Se borra el canal sembrado dentro de la transacción de este test -- se
        # revierte solo al terminar, no afecta a otros tests.
        await db_session.execute(delete(ChannelModel).where(ChannelModel.name == ChannelName.CALL_IA))
        await db_session.flush()

        channel = await repo.get_by_name(ChannelName.CALL_IA)

        assert channel is None
