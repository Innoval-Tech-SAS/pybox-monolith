"""Acceso a datos del vínculo entre ticket de soporte y pago/crédito."""

import uuid

from sqlalchemy import select

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.payments.models.payment_ticket_model import PaymentTicketModel


class PaymentTicketRepository(SoftDeleteRepositoryBase[PaymentTicketModel]):
    model_class = PaymentTicketModel

    async def get_by_ticket_id(self, ticket_id: uuid.UUID) -> PaymentTicketModel | None:
        result = await self.session.execute(
            select(PaymentTicketModel).where(PaymentTicketModel.ticket_id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def has_open_request_for_payment(self, payment_id: uuid.UUID) -> bool:
        """True si el pago ya tiene un vínculo (solicitud) registrado. Se usa junto con
        el estado del pago para bloquear solicitudes duplicadas."""
        result = await self.session.execute(
            select(PaymentTicketModel.id)
            .where(PaymentTicketModel.payment_id == payment_id)
            .limit(1)
        )
        return result.scalar_one_or_none() is not None
