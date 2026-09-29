import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from billing.invoices.models.payment_attempt_model import InvoicePaymentAttemptModel


class InvoicePaymentAttemptRepository(SoftDeleteRepositoryBase[InvoicePaymentAttemptModel]):
    model_class = InvoicePaymentAttemptModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_latest_by_invoice_id(self, invoice_id: uuid.UUID) -> InvoicePaymentAttemptModel | None:
        result = await self.session.execute(
            select(InvoicePaymentAttemptModel)
            .where(InvoicePaymentAttemptModel.invoice_id == invoice_id, InvoicePaymentAttemptModel.deleted_at.is_(None))
            .order_by(InvoicePaymentAttemptModel.attempt_number.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def get_by_provider_reference(
        self, provider_reference: str, *, for_update: bool = False
    ) -> InvoicePaymentAttemptModel | None:
        query = select(InvoicePaymentAttemptModel).where(
            InvoicePaymentAttemptModel.provider_reference == provider_reference,
            InvoicePaymentAttemptModel.deleted_at.is_(None),
        )
        if for_update:
            query = query.with_for_update()
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_provider_link_id(
        self, provider_link_id: str, *, for_update: bool = False
    ) -> InvoicePaymentAttemptModel | None:
        query = select(InvoicePaymentAttemptModel).where(
            InvoicePaymentAttemptModel.provider_link_id == provider_link_id,
            InvoicePaymentAttemptModel.deleted_at.is_(None),
        )
        if for_update:
            query = query.with_for_update()
        result = await self.session.execute(query)
        return result.scalars().first()
