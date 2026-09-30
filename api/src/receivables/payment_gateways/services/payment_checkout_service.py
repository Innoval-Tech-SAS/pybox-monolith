"""Creación de transacciones de cobro (checkout) contra la pasarela de cobro."""

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status

from identity.users.schemas.user_session_schema import UserSession
from receivables.payment_gateways.enums.payment_gateway_enums import (
    ChargeMode,
    ReceivablesGatewayProvider,
)
from receivables.payment_gateways.gateways.base import PaymentMethodInput
from receivables.payment_gateways.gateways.resolver import ReceivablesGatewayResolver
from receivables.payment_gateways.models.payment_attempt_model import (
    CreditPaymentAttemptModel,
)
from receivables.payment_gateways.repository.payment_attempt_repository import (
    CreditPaymentAttemptRepository,
)
from receivables.payment_gateways.utils.reference_utils import (
    build_payment_reference,
    to_amount_in_cents,
)
from receivables.payment_gateways.utils.wompi_status_mapping import to_attempt_status
from receivables.payments.services.payment_ownership_resolver import (
    PaymentOwnershipResolver,
)

_CURRENCY = "COP"


class PaymentCheckoutService:
    """Autoservicio del titular (scope SELF): inicia un cobro puntual (`CHECKOUT`, el
    deudor esta presente y confirma) de UNA cuota pendiente contra la pasarela de la
    organizacion dueña del credito. Reutiliza `PaymentOwnershipResolver` — misma cadena
    de pertenencia que `PaymentSelfServiceService` (ver skill `tenant-isolation`)."""

    def __init__(
        self,
        ownership_resolver: PaymentOwnershipResolver,
        attempt_repo: CreditPaymentAttemptRepository,
        gateway_resolver: ReceivablesGatewayResolver,
    ) -> None:
        self._ownership_resolver = ownership_resolver
        self._attempt_repo = attempt_repo
        self._gateway_resolver = gateway_resolver

    async def create_transaction(
        self,
        session: UserSession,
        payment_id: uuid.UUID,
        payment_method: PaymentMethodInput,
        customer_email: str,
    ) -> CreditPaymentAttemptModel:
        (
            payment,
            _credit,
            portfolio,
        ) = await self._ownership_resolver.resolve_owned_payment(session, payment_id)

        gateway = await self._gateway_resolver.get_for_organization(
            portfolio.organization_id, ReceivablesGatewayProvider.WOMPI
        )
        if gateway is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Esta organización no tiene una pasarela de pago configurada.",
            )

        tokens = await gateway.get_acceptance_tokens()

        latest_attempt = await self._attempt_repo.get_latest_by_payment_id(payment.id)
        attempt_number = (latest_attempt.attempt_number + 1) if latest_attempt else 1
        amount_in_cents = to_amount_in_cents(payment.payment_amount)
        reference = build_payment_reference(payment.id, attempt_number)

        transaction = await gateway.create_transaction(
            reference=reference,
            amount_in_cents=amount_in_cents,
            currency=_CURRENCY,
            payment_method=payment_method,
            acceptance_token=tokens.acceptance_token,
            accept_personal_auth=tokens.personal_data_token,
            customer_email=customer_email,
        )

        return await self._attempt_repo.add(
            CreditPaymentAttemptModel(
                payment_id=payment.id,
                attempt_number=attempt_number,
                provider=ReceivablesGatewayProvider.WOMPI,
                charge_mode=ChargeMode.CHECKOUT,
                provider_reference=reference,
                provider_transaction_id=transaction.id,
                expected_amount_cents=amount_in_cents,
                status=to_attempt_status(transaction.status),
                provider_payload=transaction.raw,
                acceptance_permalink=tokens.acceptance_permalink,
                personal_data_permalink=tokens.personal_data_permalink,
                accepted_at=datetime.now(timezone.utc),
            )
        )
