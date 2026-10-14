"""Fixtures/helpers compartidos por los tests de repositorio de `messaging.campaigns`
(campaign_repository/campaign_time_repository/campaign_result_repository). No son
fixtures de pytest (salvo donde se indica): permiten crear varias campañas/canales
distintos dentro del mismo test sin acoplarse entre archivos.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from messaging.campaigns.enums.campaign_enums import CampaignStatus
from messaging.campaigns.models.campaign_model import CampaignModel
from messaging.channels.enums.channel_enums import ChannelName
from messaging.channels.models.channel_model import ChannelModel


async def get_channel_id(
    db_session: AsyncSession, name: ChannelName = ChannelName.SMS
) -> uuid.UUID:
    """El canal ya viene sembrado por `_prepared_database` (ver tests/conftest.py,
    `seed_channels`) -- se reutiliza en vez de insertar uno nuevo y chocar con el
    `unique=True` de `canales.nombre`."""
    result = await db_session.execute(
        select(ChannelModel).where(ChannelModel.name == name)
    )
    channel = result.scalar_one()
    return channel.id


def build_campaign(
    portfolio_id: uuid.UUID, channel_id: uuid.UUID, **overrides
) -> CampaignModel:
    defaults = dict(
        name=f"Campaña {uuid.uuid4().hex[:8]}",
        message="hola",
        status=CampaignStatus.DRAFT,
        portfolio_id=portfolio_id,
        channel_id=channel_id,
    )
    defaults.update(overrides)
    return CampaignModel(**defaults)
