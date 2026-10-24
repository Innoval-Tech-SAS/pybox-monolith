"""BoldWebhookService: organización sin credenciales -> 404 genérico; firma inválida
-> 401; sin `metadata.reference` -> no hace nada; reference conocida -> reconsulta el
estado real contra Bold y sincroniza el intento -- mismo criterio que
`test_wompi_webhook_service.py`, pero la firma de Bold se verifica sobre bytes crudos
más un header, no sobre el `dict` ya parseado."""

import base64
import hashlib
import hmac
import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock

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
from receivables.payment_gateways.services.bold_webhook_service import (
    BoldWebhookService,
)
from receivables.payment_gateways.services.payment_gateway_credential_service import (
    DecryptedGatewayCredential,
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

_SECRET_KEY = "test-secret"
_BODY = {"data": {"metadata": {"reference": "PAG-TEST-1"}}}


def _raw_body() -> bytes:
    return json.dumps(_BODY).encode("utf-8")


def _valid_signature(raw_body: bytes) -> str:
    encoded = base64.b64encode(raw_body)
    return hmac.new(_SECRET_KEY.encode("utf-8"), encoded, hashlib.sha256).hexdigest()


def _credentials(organization_id: uuid.UUID, secret_key: str = _SECRET_KEY):
    return DecryptedGatewayCredential(
        organization_id=organization_id,
        provider=ReceivablesGatewayProvider.BOLD,
        values={"identity_key": "id-key", "secret_key": secret_key},
        lookup_key=None,
    )


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
        provider=ReceivablesGatewayProvider.BOLD,
        charge_mode=ChargeMode.CHECKOUT,
        provider_reference="PAG-TEST-1",
        provider_transaction_id="PAG-TEST-1",
        expected_amount_cents=expected_amount_cents,
        status=attempt_status,
    )
    db_session.add(attempt)
    await db_session.flush()
    return org, payment, attempt


def make_service(
    db_session, credential_service, gateway_resolver
) -> BoldWebhookService:
    return BoldWebhookService(
        credential_service,
        gateway_resolver,
        CreditPaymentAttemptRepository(db_session),
        PaymentRepository(db_session),
    )


class TestBoldWebhookService:
    async def test_organization_without_credentials_raises_404(self, db_session):
        credential_service = AsyncMock()
        credential_service.get_decrypted = AsyncMock(return_value=None)
        service = make_service(db_session, credential_service, AsyncMock())

        with pytest.raises(HTTPException) as exc_info:
            await service.process_webhook(uuid.uuid4(), _raw_body(), "whatever")
        assert exc_info.value.status_code == 404

    async def test_invalid_signature_raises_401(self, db_session):
        org = await add_organization(db_session)
        credential_service = AsyncMock()
        credential_service.get_decrypted = AsyncMock(return_value=_credentials(org.id))
        service = make_service(db_session, credential_service, AsyncMock())

        with pytest.raises(HTTPException) as exc_info:
            await service.process_webhook(org.id, _raw_body(), "firma-invalida")
        assert exc_info.value.status_code == 401

    async def test_missing_reference_does_nothing(self, db_session):
        org = await add_organization(db_session)
        credential_service = AsyncMock()
        credential_service.get_decrypted = AsyncMock(return_value=_credentials(org.id))
        service = make_service(db_session, credential_service, AsyncMock())

        raw_body = json.dumps({"data": {}}).encode("utf-8")
        await service.process_webhook(org.id, raw_body, _valid_signature(raw_body))

    async def test_approved_matching_amount_marks_payment_paid(self, db_session):
        org, payment, attempt = await _setup_payment_and_attempt(
            db_session, expected_amount_cents=1_500_000
        )
        credential_service = AsyncMock()
        credential_service.get_decrypted = AsyncMock(return_value=_credentials(org.id))

        transaction = GatewayTransaction(
            id="PAG-TEST-1",
            status="APPROVED",
            amount_in_cents=1_500_000,
            currency="COP",
            reference="PAG-TEST-1",
            payment_method_type="CREDIT_CARD",
            raw={},
        )
        gateway = AsyncMock()
        gateway.get_transaction = AsyncMock(return_value=transaction)
        gateway_resolver = AsyncMock()
        gateway_resolver.get_for_organization = AsyncMock(return_value=gateway)
        service = make_service(db_session, credential_service, gateway_resolver)

        raw_body = _raw_body()
        await service.process_webhook(org.id, raw_body, _valid_signature(raw_body))

        await db_session.refresh(attempt)
        await db_session.refresh(payment)
        assert attempt.status == ReceivablesPaymentAttemptStatus.APPROVED
        assert payment.status == PaymentStatus.PAID
