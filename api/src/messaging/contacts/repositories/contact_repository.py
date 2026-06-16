import uuid
from typing import Sequence

from sqlalchemy import select

from core.base.repository_base import RepositoryBase
from messaging.channels.enums.channel_enums import ChannelName
from messaging.channels.models.channel_model import ChannelModel
from messaging.contacts.enums.contact_enums import ContactStatus, ProviderType
from messaging.contacts.models.contact_model import ContactModel


class ContactRepository(RepositoryBase[ContactModel]):
    model_class = ContactModel

    async def get_by_debtor(
        self,
        debtor_id: int,
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
