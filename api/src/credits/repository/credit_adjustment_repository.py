from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.soft_delete_repository_base import SoftDeleteRepositoryBase
from credits.models.credit_adjustment_model import CreditAdjustmentModel


class CreditAdjustmentRepository(SoftDeleteRepositoryBase[CreditAdjustmentModel]):
    model_class = CreditAdjustmentModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_credit_id(self, credit_id: int) -> list[CreditAdjustmentModel]:
        result = await self.session.execute(
            select(CreditAdjustmentModel).where(
                CreditAdjustmentModel.credit_id == credit_id,
                CreditAdjustmentModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())
