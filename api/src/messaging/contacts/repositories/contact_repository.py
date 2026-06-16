import uuid
from typing import Sequence

from sqlalchemy import select

from core.base.repository_base import RepositoryBase
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

    async def get_by_provider_id(self, provider_id: str) -> ContactModel | None:
        result = await self.session.execute(
            select(ContactModel).where(ContactModel.provider_id == provider_id)
        )
        return result.scalar_one_or_none()
