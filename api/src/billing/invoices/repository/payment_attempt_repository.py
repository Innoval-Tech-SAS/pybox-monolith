import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from billing.invoices.models.payment_attempt_model import PaymentAttemptModel


class PaymentAttemptRepository(SoftDeleteRepositoryBase[PaymentAttemptModel]):
    model_class = PaymentAttemptModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_latest_by_invoice_id(self, invoice_id: uuid.UUID) -> PaymentAttemptModel | None:
        result = await self.session.execute(
            select(PaymentAttemptModel)
            .where(PaymentAttemptModel.invoice_id == invoice_id, PaymentAttemptModel.deleted_at.is_(None))
            .order_by(PaymentAttemptModel.attempt_number.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def get_by_bold_reference(self, bold_reference: str) -> PaymentAttemptModel | None:
        result = await self.session.execute(
            select(PaymentAttemptModel).where(
                PaymentAttemptModel.bold_reference == bold_reference,
                PaymentAttemptModel.deleted_at.is_(None),
            )
        )
        return result.scalars().first()
