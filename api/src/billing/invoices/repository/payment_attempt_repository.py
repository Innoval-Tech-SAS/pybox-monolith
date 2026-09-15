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

    async def get_by_provider_reference(
        self, provider_reference: str, *, for_update: bool = False
    ) -> PaymentAttemptModel | None:
        query = select(PaymentAttemptModel).where(
            PaymentAttemptModel.provider_reference == provider_reference,
            PaymentAttemptModel.deleted_at.is_(None),
        )
        if for_update:
            query = query.with_for_update()
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_provider_link_id(
        self, provider_link_id: str, *, for_update: bool = False
    ) -> PaymentAttemptModel | None:
        query = select(PaymentAttemptModel).where(
            PaymentAttemptModel.provider_link_id == provider_link_id,
            PaymentAttemptModel.deleted_at.is_(None),
        )
        if for_update:
            query = query.with_for_update()
        result = await self.session.execute(query)
        return result.scalars().first()
