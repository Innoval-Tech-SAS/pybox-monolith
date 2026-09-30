"""Endpoints de checkout: fuentes de pago guardadas y creación de transacciones."""

import uuid

from fastapi import status

from core.config.api_router import APIRouter
from receivables.payment_gateways.dependencies import (
    PaymentCheckoutServiceDep,
    PaymentSourceServiceDep,
    RequireSelfForPaymentGateways,
)
from receivables.payment_gateways.gateways.base import (
    BancolombiaTransferPaymentMethod,
    CardPaymentMethod,
    NequiPaymentMethod,
    PaymentMethodInput,
    PsePaymentMethod,
)
from receivables.payment_gateways.schemas.payment_checkout_schemas import (
    BancolombiaTransferTransactionRequest,
    CardTransactionRequest,
    NequiTransactionRequest,
    PaymentAttemptResponse,
    PaymentSourceResponse,
    PseTransactionRequest,
    TokenizeCardSourceRequest,
    TokenizeNequiSourceRequest,
    TransactionRequest,
)

router = APIRouter(prefix="/credits/payments", tags=["Cobro de cuotas (Wompi)"])


def _to_gateway_payment_method(body: TransactionRequest) -> PaymentMethodInput:
    if isinstance(body, CardTransactionRequest):
        return CardPaymentMethod(token=body.token, installments=body.installments)
    if isinstance(body, PseTransactionRequest):
        return PsePaymentMethod(
            user_type=body.user_type,
            user_legal_id_type=body.user_legal_id_type,
            user_legal_id=body.user_legal_id,
            financial_institution_code=body.financial_institution_code,
            payment_description=body.payment_description,
        )
    if isinstance(body, NequiTransactionRequest):
        return NequiPaymentMethod(phone_number=body.phone_number)
    if isinstance(body, BancolombiaTransferTransactionRequest):
        return BancolombiaTransferPaymentMethod(
            payment_description=body.payment_description
        )
    raise ValueError(f"Tipo de método de pago no soportado: {type(body)!r}")


@router.post(
    "/{payment_id}/wompi/transaction",
    response_model=PaymentAttemptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar el cobro de una cuota vía Wompi",
)
async def create_transaction(
    payment_id: uuid.UUID,
    body: TransactionRequest,
    session: RequireSelfForPaymentGateways,
    service: PaymentCheckoutServiceDep,
) -> PaymentAttemptResponse:
    attempt = await service.create_transaction(
        session, payment_id, _to_gateway_payment_method(body), body.customer_email
    )
    return PaymentAttemptResponse(
        id=attempt.id,
        status=attempt.status.value,
        provider_reference=attempt.provider_reference,
        provider_transaction_id=attempt.provider_transaction_id,
        charge_mode=attempt.charge_mode.value,
    )


@router.post(
    "/{payment_id}/wompi/payment-sources/card",
    response_model=PaymentSourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Guardar una tarjeta como fuente de pago reutilizable (cobro automático)",
)
async def create_card_source(
    payment_id: uuid.UUID,
    body: TokenizeCardSourceRequest,
    session: RequireSelfForPaymentGateways,
    service: PaymentSourceServiceDep,
) -> PaymentSourceResponse:
    source = await service.create_card_source(
        session,
        payment_id,
        body.number,
        body.cvc,
        body.exp_month,
        body.exp_year,
        body.card_holder,
        body.customer_email,
    )
    return _to_source_response(source)


@router.post(
    "/{payment_id}/wompi/payment-sources/nequi",
    response_model=PaymentSourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Guardar Nequi como fuente de pago reutilizable (cobro automático)",
)
async def create_nequi_source(
    payment_id: uuid.UUID,
    body: TokenizeNequiSourceRequest,
    session: RequireSelfForPaymentGateways,
    service: PaymentSourceServiceDep,
) -> PaymentSourceResponse:
    source = await service.create_nequi_source(
        session, payment_id, body.phone_number, body.customer_email
    )
    return _to_source_response(source)


@router.get(
    "/{payment_id}/wompi/payment-sources",
    response_model=list[PaymentSourceResponse],
    summary="Listar mis fuentes de pago guardadas",
)
async def list_payment_sources(
    payment_id: uuid.UUID,
    session: RequireSelfForPaymentGateways,
    service: PaymentSourceServiceDep,
) -> list[PaymentSourceResponse]:
    sources = await service.list_active(session, payment_id)
    return [_to_source_response(source) for source in sources]


@router.delete(
    "/{payment_id}/wompi/payment-sources/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revocar una fuente de pago guardada",
)
async def revoke_payment_source(
    payment_id: uuid.UUID,
    source_id: uuid.UUID,
    session: RequireSelfForPaymentGateways,
    service: PaymentSourceServiceDep,
) -> None:
    await service.revoke(session, payment_id, source_id)


def _to_source_response(source) -> PaymentSourceResponse:
    return PaymentSourceResponse(
        id=source.id,
        type=source.type.value,
        status=source.status.value,
        masked_identifier=source.masked_identifier,
        brand=source.brand,
        is_active=source.is_active,
    )
