"""Aplica sobre las cuotas el resultado de un ticket de autogestión de pago."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from receivables.payments.enums.payment_enums import PaymentStatus
from receivables.payments.models.payment_model import PaymentModel
from receivables.payments.repository.payment_repository import PaymentRepository
from receivables.payments.repository.payment_ticket_repository import (
    PaymentTicketRepository,
)


class PaymentResolutionService:
    """Aplica sobre las cuotas el resultado de resolver un ticket de autogestión de
    pago (reprogramación / validación). Lo invoca `SupportService` al resolver el
    ticket: la mutación del dominio de pagos vive aquí, no dentro de soporte.

    No depende de soporte (evita el ciclo con PaymentSelfServiceService, que sí usa
    SupportService para crear tickets)."""

    def __init__(self, session: AsyncSession) -> None:
        self._payment_repo = PaymentRepository(session)
        self._payment_ticket_repo = PaymentTicketRepository(session)

    async def apply_reschedule_resolution(
        self, ticket_id: uuid.UUID, approved: bool
    ) -> None:
        link = await self._payment_ticket_repo.get_by_ticket_id(ticket_id)
        if link is None:
            return
        payment = await self._payment_repo.get_by_id(link.payment_id)
        if payment is None:
            return

        if not approved:
            payment.status = PaymentStatus.PENDING
            await self._payment_repo.update(payment)
            return

        # Aprobado: la cuota actual queda REPROGRAMADA y se crea una nueva cuota
        # PENDIENTE en la fecha elegida, copiando el monto y desglose actuales.
        payment.status = PaymentStatus.RESCHEDULED
        new_payment = self._clone_payment_for_reschedule(payment, link.requested_date)
        created = await self._payment_repo.add(new_payment)
        link.new_payment_id = created.id
        await self._payment_ticket_repo.update(link)
        await self._payment_repo.update(payment)

    async def apply_validation_resolution(
        self, ticket_id: uuid.UUID, approved: bool
    ) -> None:
        link = await self._payment_ticket_repo.get_by_ticket_id(ticket_id)
        if link is None:
            return
        payment = await self._payment_repo.get_by_id(link.payment_id)
        if payment is None:
            return

        if not approved:
            payment.status = PaymentStatus.PENDING
            await self._payment_repo.update(payment)
            return

        # Aprobado: el pago se marca como realizado con fecha = cargue del comprobante.
        payment.status = PaymentStatus.PAID
        payment.payment_date = link.created_at
        await self._payment_repo.update(payment)

    @staticmethod
    def _clone_payment_for_reschedule(payment: PaymentModel, new_date) -> PaymentModel:
        return PaymentModel(
            limit_pay_date=new_date,
            payment_date=None,
            payment_amount=payment.payment_amount,
            installment_number=payment.installment_number,
            principal_payment=payment.principal_payment,
            current_interest_amount=payment.current_interest_amount,
            overdue_interest_amount=payment.overdue_interest_amount,
            life_insurance_charge=payment.life_insurance_charge,
            vehicle_insurance_charge=payment.vehicle_insurance_charge,
            insurances_total=payment.insurances_total,
            other_charges=payment.other_charges,
            total_interest_amount=payment.total_interest_amount,
            other_concepts_amount=payment.other_concepts_amount,
            vat=payment.vat,
            commission_amount=payment.commission_amount,
            platform_fee=payment.platform_fee,
            condonation_amount=payment.condonation_amount,
            discount_amount=payment.discount_amount,
            amount_uvr=payment.amount_uvr,
            uvr_quote_at_payment=payment.uvr_quote_at_payment,
            credit_id=payment.credit_id,
            status=PaymentStatus.PENDING,
        )
