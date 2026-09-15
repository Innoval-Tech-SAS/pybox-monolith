import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.repository_base import RepositoryBase
from receivables.payments.models.payment_ticket_model import PaymentTicketModel


class PaymentTicketRepository(RepositoryBase[PaymentTicketModel]):
    model_class = PaymentTicketModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_ticket_id(self, ticket_id: uuid.UUID) -> PaymentTicketModel | None:
        result = await self.session.execute(
            select(PaymentTicketModel).where(PaymentTicketModel.ticket_id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def has_open_request_for_payment(self, payment_id: uuid.UUID) -> bool:
        """True si el pago ya tiene un vínculo (solicitud) registrado. Se usa junto con
        el estado del pago para bloquear solicitudes duplicadas."""
        result = await self.session.execute(
            select(PaymentTicketModel.id).where(PaymentTicketModel.payment_id == payment_id).limit(1)
        )
        return result.scalar_one_or_none() is not None
