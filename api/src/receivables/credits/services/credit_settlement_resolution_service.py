"""Aplica el resultado de un ticket de liquidación (settlement) sobre el crédito."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from receivables.credits.repository.credit_repository import CreditRepository
from receivables.credits.repository.credit_settlement_ticket_repository import (
    CreditSettlementTicketRepository,
)
from receivables.payments.enums.payment_enums import PaymentStatus
from receivables.payments.models.payment_model import PaymentModel
from receivables.payments.repository.payment_repository import PaymentRepository


class CreditSettlementResolutionService:
    """Aplica el resultado de resolver un ticket de baja de crédito. Lo invoca
    `SupportService` al resolver el ticket: la mutación de créditos/pagos vive aquí,
    no dentro de soporte.

    No depende de soporte (evita el ciclo con CreditSelfServiceService, que sí usa
    SupportService para crear el ticket)."""

    def __init__(self, session: AsyncSession) -> None:
        self._credit_repo = CreditRepository(session)
        self._payment_repo = PaymentRepository(session)
        self._settlement_ticket_repo = CreditSettlementTicketRepository(session)

    async def apply_settlement_resolution(
        self, ticket_id: uuid.UUID, approved: bool
    ) -> None:
        link = await self._settlement_ticket_repo.get_by_ticket_id(ticket_id)
        if link is None:
            return
        credit = await self._credit_repo.get_by_id(link.credit_id)
        if credit is None:
            return

        if not approved:
            # Rechazado: el crédito sigue activo; el ticket ya queda resuelto/denegado.
            return

        now = datetime.now(timezone.utc)
        payment = await self._payment_repo.add(
            PaymentModel(
                credit_id=credit.id,
                limit_pay_date=now,
                payment_date=now,
                payment_amount=link.settlement_amount,
                principal_payment=link.settlement_amount,
                installment_number=None,
                status=PaymentStatus.PAID,
            )
        )
        link.payment_id = payment.id
        await self._settlement_ticket_repo.update(link)

        credit.is_active = False
        await self._credit_repo.update(credit)
