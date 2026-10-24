"""EpaycoWebhookService: organización sin credenciales -> 404 genérico; firma inválida
-> 401; sin `x_ref_payco` -> no hace nada; referencia conocida -> reconsulta el estado
real contra ePayco y sincroniza el intento -- mismo criterio que
`test_payu_webhook_service.py`. A diferencia de PayU, el intento se busca por
`provider_transaction_id` (ePayco solo conoce su propio `ref_payco`, nunca acepta una
referencia nuestra al crear la transacción)."""

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
from receivables.payment_gateways.gateways.base import GatewayTransaction
from receivables.payment_gateways.models.payment_attempt_model import (
    CreditPaymentAttemptModel,
)
from receivables.payment_gateways.repository.payment_attempt_repository import (
    CreditPaymentAttemptRepository,
)
from receivables.payment_gateways.services.epayco_webhook_service import (
    EpaycoWebhookService,
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

_CONFIRMATION_FIELDS = {
    "x_cust_id_cliente": "28770",
    "x_ref_payco": "26291500",
    "x_transaction_id": "705885651",
    "x_amount": "15000",
    "x_currency_code": "COP",
    "x_signature": "whatever",
}


_PENDING = ReceivablesPaymentAttemptStatus.PENDING


async def _setup_payment_and_attempt(
    db_session,
    *,
    expected_amount_cents: int = 1_500_000,
    attempt_status: ReceivablesPaymentAttemptStatus = _PENDING,
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
        provider=ReceivablesGatewayProvider.EPAYCO,
        charge_mode=ChargeMode.CHECKOUT,
        provider_reference="PAG-TEST-1",
        provider_transaction_id="26291500",
        expected_amount_cents=expected_amount_cents,
        status=attempt_status,
    )
    db_session.add(attempt)
    await db_session.flush()
    return org, payment, attempt


def make_gateway(
    *, signature_valid: bool, transaction: GatewayTransaction
) -> MagicMock:
    gateway = MagicMock()
    gateway.verify_webhook_signature = MagicMock(return_value=signature_valid)
    gateway.get_transaction = AsyncMock(return_value=transaction)
    return gateway


def make_service(db_session, gateway_resolver) -> EpaycoWebhookService:
    return EpaycoWebhookService(
        gateway_resolver,
        CreditPaymentAttemptRepository(db_session),
        PaymentRepository(db_session),
    )


class TestEpaycoWebhookService:
    async def test_organization_without_credentials_raises_404(self, db_session):
        gateway_resolver = AsyncMock()
        gateway_resolver.get_for_organization = AsyncMock(return_value=None)
        service = make_service(db_session, gateway_resolver)

        with pytest.raises(HTTPException) as exc_info:
            await service.process_confirmation(uuid.uuid4(), _CONFIRMATION_FIELDS)
        assert exc_info.value.status_code == 404

    async def test_invalid_signature_raises_401(self, db_session):
        org = await add_organization(db_session)
        transaction = GatewayTransaction(
            id="26291500",
            status="APPROVED",
            amount_in_cents=1_500_000,
            currency="COP",
            reference="26291500",
            payment_method_type="PSE",
            raw={},
        )
        gateway = make_gateway(signature_valid=False, transaction=transaction)
        gateway_resolver = AsyncMock()
        gateway_resolver.get_for_organization = AsyncMock(return_value=gateway)
        service = make_service(db_session, gateway_resolver)

        with pytest.raises(HTTPException) as exc_info:
            await service.process_confirmation(org.id, _CONFIRMATION_FIELDS)
        assert exc_info.value.status_code == 401

    async def test_missing_ref_payco_does_nothing(self, db_session):
        org = await add_organization(db_session)
        gateway = make_gateway(
            signature_valid=True,
            transaction=GatewayTransaction(
                id="",
                status="APPROVED",
                amount_in_cents=0,
                currency="COP",
                reference="",
                payment_method_type="PSE",
                raw={},
            ),
        )
        gateway_resolver = AsyncMock()
        gateway_resolver.get_for_organization = AsyncMock(return_value=gateway)
        service = make_service(db_session, gateway_resolver)

        fields = {**_CONFIRMATION_FIELDS, "x_ref_payco": ""}
        await service.process_confirmation(org.id, fields)

    async def test_approved_matching_amount_marks_payment_paid(self, db_session):
        org, payment, attempt = await _setup_payment_and_attempt(
            db_session, expected_amount_cents=1_500_000
        )
        transaction = GatewayTransaction(
            id="26291500",
            status="APPROVED",
            amount_in_cents=1_500_000,
            currency="COP",
            reference="26291500",
            payment_method_type="PSE",
            raw={},
        )
        gateway = make_gateway(signature_valid=True, transaction=transaction)
        gateway_resolver = AsyncMock()
        gateway_resolver.get_for_organization = AsyncMock(return_value=gateway)
        service = make_service(db_session, gateway_resolver)

        await service.process_confirmation(org.id, _CONFIRMATION_FIELDS)

        await db_session.refresh(attempt)
        await db_session.refresh(payment)
        assert attempt.status == ReceivablesPaymentAttemptStatus.APPROVED
        assert payment.status == PaymentStatus.PAID
