"""WompiWebhookService: organización sin credenciales -> 404 genérico; firma inválida
-> 401; monto reportado != esperado -> el intento queda ERROR y la cuota NO se marca
pagada; monto correcto -> cuota PAGADA; una segunda entrega sobre un intento ya
APPROVED no reprocesa (idempotencia). El gateway se mockea (nunca pega HTTP real a
Wompi); intento/pago son reales contra la DB de test -- mismo criterio que
`test_invoice_service.py` para `mark_attempt_paid`."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from receivables.payment_gateways.enums.payment_gateway_enums import (
    ChargeMode,
    ReceivablesGatewayProvider,
    ReceivablesPaymentAttemptStatus,
)
from receivables.payment_gateways.gateways.base import WompiTransaction
from receivables.payment_gateways.models.payment_attempt_model import (
    CreditPaymentAttemptModel,
)
from receivables.payment_gateways.repository.payment_attempt_repository import (
    CreditPaymentAttemptRepository,
)
from receivables.payment_gateways.services.payment_webhook_service import (
    WompiWebhookService,
)
from receivables.payments.enums.payment_enums import PaymentStatus
from receivables.payments.models.payment_model import PaymentModel
from receivables.payments.repository.payment_repository import PaymentRepository
from tests.receivables.conftest import (
    add_organization,
    build_credit,
    build_debtor,
    build_portfolio,
)

_WEBHOOK_BODY = {"data": {"transaction": {"id": "txn-1"}}}


async def _setup_payment_and_attempt(
    db_session,
    *,
    expected_amount_cents: int = 1_500_000,
    attempt_status: ReceivablesPaymentAttemptStatus = ReceivablesPaymentAttemptStatus.PENDING,
):
    org = await add_organization(db_session)
    portfolio = build_portfolio(org.id)
    db_session.add(portfolio)
    await db_session.flush()
    debtor = build_debtor(org.id)
    db_session.add(debtor)
    await db_session.flush()
    credit = build_credit(portfolio.id, debtor.id, is_active=True)
    db_session.add(credit)
    await db_session.flush()
    payment = PaymentModel(
        limit_pay_date=datetime.now(timezone.utc),
        payment_amount=Decimal("15000.00"),
        principal_payment=Decimal("12000.00"),
        total_interest_amount=Decimal("3000.00"),
        status=PaymentStatus.PENDING,
        credit_id=credit.id,
    )
    db_session.add(payment)
    await db_session.flush()
    attempt = CreditPaymentAttemptModel(
        payment_id=payment.id,
        attempt_number=1,
        provider=ReceivablesGatewayProvider.WOMPI,
        charge_mode=ChargeMode.CHECKOUT,
        provider_reference="PAG-TEST-1",
        provider_transaction_id="txn-1",
        expected_amount_cents=expected_amount_cents,
        status=attempt_status,
    )
    db_session.add(attempt)
    await db_session.flush()
    return org, payment, attempt


def make_gateway(*, signature_valid: bool, transaction: WompiTransaction) -> MagicMock:
    gateway = MagicMock()
    gateway.verify_webhook_signature = MagicMock(return_value=signature_valid)
    gateway.get_transaction = AsyncMock(return_value=transaction)
    return gateway


def make_service(db_session, gateway_resolver) -> WompiWebhookService:
    return WompiWebhookService(
        gateway_resolver,
        CreditPaymentAttemptRepository(db_session),
        PaymentRepository(db_session),
    )


class TestWompiWebhookService:
    async def test_organization_without_credentials_raises_404(self, db_session):
        gateway_resolver = AsyncMock()
        gateway_resolver.get_for_organization = AsyncMock(return_value=None)
        service = make_service(db_session, gateway_resolver)

        with pytest.raises(HTTPException) as exc_info:
            await service.process_webhook(uuid.uuid4(), _WEBHOOK_BODY)
        assert exc_info.value.status_code == 404

    async def test_invalid_signature_raises_401(self, db_session):
        org = await add_organization(db_session)
        transaction = WompiTransaction(
            id="txn-1",
            status="APPROVED",
            amount_in_cents=1_500_000,
            currency="COP",
            reference="PAG-TEST-1",
            payment_method_type="CARD",
            raw={},
        )
        gateway = make_gateway(signature_valid=False, transaction=transaction)
        gateway_resolver = AsyncMock()
        gateway_resolver.get_for_organization = AsyncMock(return_value=gateway)
        service = make_service(db_session, gateway_resolver)

        with pytest.raises(HTTPException) as exc_info:
            await service.process_webhook(org.id, _WEBHOOK_BODY)
        assert exc_info.value.status_code == 401

    async def test_amount_mismatch_marks_attempt_error_not_payment_paid(
        self, db_session
    ):
        org, payment, attempt = await _setup_payment_and_attempt(
            db_session, expected_amount_cents=1_500_000
        )
        transaction = WompiTransaction(
            id="txn-1",
            status="APPROVED",
            amount_in_cents=999_000,
            currency="COP",
            reference="PAG-TEST-1",
            payment_method_type="CARD",
            raw={"tampered": True},
        )
        gateway = make_gateway(signature_valid=True, transaction=transaction)
        gateway_resolver = AsyncMock()
        gateway_resolver.get_for_organization = AsyncMock(return_value=gateway)
        service = make_service(db_session, gateway_resolver)

        await service.process_webhook(org.id, _WEBHOOK_BODY)

        await db_session.refresh(attempt)
        await db_session.refresh(payment)
        assert attempt.status == ReceivablesPaymentAttemptStatus.ERROR
        assert payment.status == PaymentStatus.PENDING

    async def test_approved_matching_amount_marks_payment_paid(self, db_session):
        org, payment, attempt = await _setup_payment_and_attempt(
            db_session, expected_amount_cents=1_500_000
        )
        transaction = WompiTransaction(
            id="txn-1",
            status="APPROVED",
            amount_in_cents=1_500_000,
            currency="COP",
            reference="PAG-TEST-1",
            payment_method_type="CARD",
            raw={},
        )
        gateway = make_gateway(signature_valid=True, transaction=transaction)
        gateway_resolver = AsyncMock()
        gateway_resolver.get_for_organization = AsyncMock(return_value=gateway)
        service = make_service(db_session, gateway_resolver)

        await service.process_webhook(org.id, _WEBHOOK_BODY)

        await db_session.refresh(attempt)
        await db_session.refresh(payment)
        assert attempt.status == ReceivablesPaymentAttemptStatus.APPROVED
        assert payment.status == PaymentStatus.PAID

    async def test_already_approved_attempt_is_idempotent(self, db_session):
        org, payment, attempt = await _setup_payment_and_attempt(
            db_session,
            expected_amount_cents=1_500_000,
            attempt_status=ReceivablesPaymentAttemptStatus.APPROVED,
        )
        payment.status = PaymentStatus.PAID
        await db_session.flush()

        transaction = WompiTransaction(
            id="txn-1",
            status="APPROVED",
            amount_in_cents=1_500_000,
            currency="COP",
            reference="PAG-TEST-1",
            payment_method_type="CARD",
            raw={},
        )
        gateway = make_gateway(signature_valid=True, transaction=transaction)
        gateway_resolver = AsyncMock()
        gateway_resolver.get_for_organization = AsyncMock(return_value=gateway)
        service = make_service(db_session, gateway_resolver)

        # No debe lanzar ni duplicar el efecto de una entrega anterior ya procesada.
        await service.process_webhook(org.id, _WEBHOOK_BODY)

        await db_session.refresh(attempt)
        await db_session.refresh(payment)
        assert attempt.status == ReceivablesPaymentAttemptStatus.APPROVED
        assert payment.status == PaymentStatus.PAID
