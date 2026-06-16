from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.contact_methods.models.contact_method_model import ContactMethodModel


class ContactMethodRepository(SoftDeleteRepositoryBase[ContactMethodModel]):
    model_class = ContactMethodModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_debtor_id(self, debtor_id: int) -> list[ContactMethodModel]:
        result = await self.session.execute(
            select(ContactMethodModel).where(
                ContactMethodModel.debtor_id == debtor_id,
                ContactMethodModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())
