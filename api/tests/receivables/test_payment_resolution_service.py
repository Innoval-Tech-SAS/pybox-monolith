"""Tests unitarios de `PaymentResolutionService`: las dos mutaciones que aplica al
resolver un ticket de autogestión de pago (reprogramación / validación), en sus
ramas aprobado/rechazado, más los no-ops de ticket/pago inexistente."""

import uuid
from datetime import datetime, timezone

from app_platform.support.enums.support_enums import SupportCaseType
from app_platform.support.models.support_ticket_model import SupportTicketModel
from receivables.payments.enums.payment_enums import PaymentStatus
from receivables.payments.models.payment_model import PaymentModel
from receivables.payments.models.payment_ticket_model import PaymentTicketModel
from receivables.payments.repository.payment_repository import PaymentRepository
from receivables.payments.repository.payment_ticket_repository import (
    PaymentTicketRepository,
)
from receivables.payments.services.payment_resolution_service import (
    PaymentResolutionService,
)
from tests.receivables.conftest import (
    build_credit,
    build_debtor,
    build_organization,
    build_portfolio,
)


async def _support_ticket(db_session, created_by):
    ticket = SupportTicketModel(
        case_type=SupportCaseType.REQUIREMENT, created_by=created_by
    )
    db_session.add(ticket)
    await db_session.flush()
    return ticket


async def _credit(db_session):
    org = build_organization()
    db_session.add(org)
    await db_session.flush()
    portfolio = build_portfolio(org.id)
    db_session.add(portfolio)
    await db_session.flush()
    debtor = build_debtor(org.id)
    db_session.add(debtor)
    await db_session.flush()
    credit = build_credit(portfolio.id, debtor.id)
    db_session.add(credit)
    await db_session.flush()
    return credit


async def _payment(db_session, credit_id, **overrides):
    defaults = dict(
        limit_pay_date=datetime.now(timezone.utc),
        payment_amount=100,
        installment_number=1,
        principal_payment=80,
        total_interest_amount=20,
        status=PaymentStatus.RESCHEDULE_REQUESTED,
        credit_id=credit_id,
    )
    defaults.update(overrides)
    payment = PaymentModel(**defaults)
    db_session.add(payment)
    await db_session.flush()
    return payment


async def _ticket_link(db_session, payment_id, credit_id, created_by, **overrides):
    ticket = await _support_ticket(db_session, created_by)
    defaults = dict(
        ticket_id=ticket.id,
        payment_id=payment_id,
        credit_id=credit_id,
        requested_date=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    link = PaymentTicketModel(**defaults)
    db_session.add(link)
    await db_session.flush()
    return link


class TestApplyRescheduleResolution:
    async def test_unknown_ticket_is_a_no_op(self, db_session):
        service = PaymentResolutionService(db_session)
        await service.apply_reschedule_resolution(
            uuid.uuid4(), approved=True
        )  # no debe lanzar

    async def test_payment_missing_is_a_no_op(self, db_session, real_admin_user_id):
        credit = await _credit(db_session)
        payment = await _payment(db_session, credit.id)
        link = await _ticket_link(db_session, payment.id, credit.id, real_admin_user_id)
        # Soft-delete (no hard delete): `ticket_pago_credito.id_pago` es FK sin
        # ondelete, y `PaymentRepository.get_by_id` filtra por `deleted_at` -- así
        # se simula "pago inexistente" tal como lo ve el service en producción.
        await PaymentRepository(db_session).delete(payment)

        service = PaymentResolutionService(db_session)
        await service.apply_reschedule_resolution(
            link.ticket_id, approved=True
        )  # no debe lanzar

    async def test_rejected_reverts_payment_to_pending(
        self, db_session, real_admin_user_id
    ):
        credit = await _credit(db_session)
        payment = await _payment(db_session, credit.id)
        link = await _ticket_link(db_session, payment.id, credit.id, real_admin_user_id)

        service = PaymentResolutionService(db_session)
        await service.apply_reschedule_resolution(link.ticket_id, approved=False)

        await db_session.refresh(payment)
        assert payment.status == PaymentStatus.PENDING

    async def test_approved_marks_rescheduled_and_creates_new_pending_payment(
        self, db_session, real_admin_user_id
    ):
        credit = await _credit(db_session)
        new_date = datetime(2027, 1, 15, tzinfo=timezone.utc)
        payment = await _payment(
            db_session,
            credit.id,
            payment_amount=500,
            principal_payment=400,
            total_interest_amount=100,
        )
        link = await _ticket_link(
            db_session,
            payment.id,
            credit.id,
            real_admin_user_id,
            requested_date=new_date,
        )

        service = PaymentResolutionService(db_session)
        await service.apply_reschedule_resolution(link.ticket_id, approved=True)

        await db_session.refresh(payment)
        assert payment.status == PaymentStatus.RESCHEDULED

        payment_repo = PaymentRepository(db_session)
        all_payments = await payment_repo.get_by_credit_id(credit.id)
        new_payments = [p for p in all_payments if p.id != payment.id]
        assert len(new_payments) == 1
        new_payment = new_payments[0]
        assert new_payment.status == PaymentStatus.PENDING
        assert new_payment.limit_pay_date == new_date
        assert new_payment.payment_date is None
        assert float(new_payment.payment_amount) == 500
        assert float(new_payment.principal_payment) == 400

        ticket_repo = PaymentTicketRepository(db_session)
        refreshed_link = await ticket_repo.get_by_ticket_id(link.ticket_id)
        assert refreshed_link.new_payment_id == new_payment.id


class TestApplyValidationResolution:
    async def test_unknown_ticket_is_a_no_op(self, db_session):
        service = PaymentResolutionService(db_session)
        await service.apply_validation_resolution(
            uuid.uuid4(), approved=True
        )  # no debe lanzar

    async def test_rejected_reverts_payment_to_pending(
        self, db_session, real_admin_user_id
    ):
        credit = await _credit(db_session)
        payment = await _payment(
            db_session, credit.id, status=PaymentStatus.VALIDATION_REQUESTED
        )
        link = await _ticket_link(db_session, payment.id, credit.id, real_admin_user_id)

        service = PaymentResolutionService(db_session)
        await service.apply_validation_resolution(link.ticket_id, approved=False)

        await db_session.refresh(payment)
        assert payment.status == PaymentStatus.PENDING

    async def test_approved_marks_paid_with_ticket_creation_date(
        self, db_session, real_admin_user_id
    ):
        credit = await _credit(db_session)
        payment = await _payment(
            db_session,
            credit.id,
            status=PaymentStatus.VALIDATION_REQUESTED,
            payment_date=None,
        )
        link = await _ticket_link(db_session, payment.id, credit.id, real_admin_user_id)

        service = PaymentResolutionService(db_session)
        await service.apply_validation_resolution(link.ticket_id, approved=True)

        await db_session.refresh(payment)
        assert payment.status == PaymentStatus.PAID
        assert payment.payment_date == link.created_at
