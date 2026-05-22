from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.soft_delete_repository_base import SoftDeleteRepositoryBase
from payments.models.payment_model import PaymentModel


class PaymentRepository(SoftDeleteRepositoryBase[PaymentModel]):
    model_class = PaymentModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_credit_id(self, credit_id: int) -> list[PaymentModel]:
        result = await self.session.execute(
            select(PaymentModel).where(
                PaymentModel.credit_id == credit_id,
                PaymentModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())
