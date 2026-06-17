import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Sequence

from sqlalchemy import func, select

from core.base.repository_base import RepositoryBase
from messaging.campaigns.models.campaign_model import CampaignModel
from messaging.channels.enums.channel_enums import ChannelName
from messaging.channels.models.channel_model import ChannelModel
from messaging.contacts.enums.contact_enums import ContactStatus, ProviderType
from messaging.contacts.models.contact_model import ContactModel


@dataclass
class CampaignUsageRow:
    campaign_id: uuid.UUID
    campaign_name: str
    channel_id: uuid.UUID
    channel_name: str
    currency: str
    quantity: int
    subtotal: Decimal


class ContactRepository(RepositoryBase[ContactModel]):
    model_class = ContactModel

    async def get_billing_usage(
        self, organization_id: uuid.UUID, period_start: datetime, period_end: datetime
    ) -> list[CampaignUsageRow]:
        """
        Desglose de consumo facturable por campaña dentro del periodo [period_start, period_end).
        Solo cuenta contactos efectivamente enviados (sent_at no nulo) con precio registrado;
        el costo se suma a partir del snapshot de precio de cada envío individual, ya que el
        precio del canal puede haber cambiado durante el periodo.
        """
        stmt = (
            select(
                ContactModel.campaign_id,
                CampaignModel.name,
                ContactModel.snapshot_channel_id,
                ChannelModel.name,
                ContactModel.snapshot_currency,
                func.count(ContactModel.id),
                func.sum(ContactModel.snapshot_unit_price),
            )
            .join(CampaignModel, CampaignModel.id == ContactModel.campaign_id)
            .join(ChannelModel, ChannelModel.id == ContactModel.snapshot_channel_id)
            .where(
                ContactModel.organization_id == organization_id,
                ContactModel.sent_at.is_not(None),
                ContactModel.sent_at >= period_start,
                ContactModel.sent_at < period_end,
                ContactModel.snapshot_unit_price.is_not(None),
            )
            .group_by(
                ContactModel.campaign_id,
                CampaignModel.name,
                ContactModel.snapshot_channel_id,
                ChannelModel.name,
                ContactModel.snapshot_currency,
            )
            .order_by(CampaignModel.name)
        )
        result = await self.session.execute(stmt)
        return [
            CampaignUsageRow(
                campaign_id=campaign_id,
                campaign_name=campaign_name,
                channel_id=channel_id,
                channel_name=channel_name.value if hasattr(channel_name, "value") else channel_name,
                currency=currency or "USD",
                quantity=quantity,
                subtotal=subtotal or Decimal("0"),
            )
            for (
                campaign_id,
                campaign_name,
                channel_id,
                channel_name,
                currency,
                quantity,
                subtotal,
            ) in result.all()
        ]

    async def get_by_debtor(
        self,
        debtor_id: uuid.UUID,
        organization_id: uuid.UUID,
        portfolio_id: uuid.UUID | None = None,
    ) -> Sequence[ContactModel]:
        stmt = (
            select(ContactModel)
            .where(
                ContactModel.debtor_id == debtor_id,
                ContactModel.organization_id == organization_id,
            )
            .order_by(ContactModel.sent_at.desc().nullslast(), ContactModel.id.desc())
        )
        if portfolio_id is not None:
            stmt = stmt.where(ContactModel.portfolio_id == portfolio_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_external_id(self, external_id: str) -> ContactModel | None:
        result = await self.session.execute(
            select(ContactModel).where(ContactModel.external_id == external_id)
        )
        return result.scalar_one_or_none()

    async def get_pending_sending_ids(self) -> Sequence[tuple[str, ChannelName]]:
        stmt = (
            select(ContactModel.sending_id, ChannelModel.name)
            .join(ChannelModel, ChannelModel.id == ContactModel.snapshot_channel_id)
            .where(
                ContactModel.provider == ProviderType.NRS360,
                ContactModel.sending_id.is_not(None),
                ContactModel.status == ContactStatus.SENT,
            )
            .distinct()
        )
        result = await self.session.execute(stmt)
        return [(sending_id, channel_name) for sending_id, channel_name in result.all()]

    async def get_by_sending_id(self, sending_id: str) -> Sequence[ContactModel]:
        result = await self.session.execute(
            select(ContactModel).where(ContactModel.sending_id == sending_id)
        )
        return result.scalars().all()
