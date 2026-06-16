from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from collections.debtors.models.address_model import AddressModel


class AddressRepository(SoftDeleteRepositoryBase[AddressModel]):
    model_class = AddressModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_debtor_id(self, debtor_id: int) -> list[AddressModel]:
        result = await self.session.execute(
            select(AddressModel).where(
                AddressModel.debtor_id == debtor_id,
                AddressModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())
