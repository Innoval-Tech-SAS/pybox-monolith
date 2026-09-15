import uuid
from typing import Annotated

from fastapi import File, UploadFile, status

from core.config.api_router import APIRouter
from receivables.payments.dependencies import PaymentSelfServiceServiceDep, RequireSelf
from receivables.payments.schemas.payment_selfservice_schemas import (
    PaymentRequestResponse,
    RescheduleRequest,
)

router = APIRouter(prefix="/credits/payments", tags=["Autogestión de pagos"])


@router.post(
    "/{payment_id}/reschedule",
    response_model=PaymentRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar reprogramación de un pago",
)
async def request_reschedule(
    payment_id: uuid.UUID,
    body: RescheduleRequest,
    session: RequireSelf,
    service: PaymentSelfServiceServiceDep,
) -> PaymentRequestResponse:
    return await service.request_reschedule(session, payment_id, body.new_date)


@router.post(
    "/{payment_id}/payment-validation",
    response_model=PaymentRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Reportar un pago realizado adjuntando comprobante",
)
async def request_validation(
    payment_id: uuid.UUID,
    files: Annotated[list[UploadFile], File()],
    session: RequireSelf,
    service: PaymentSelfServiceServiceDep,
) -> PaymentRequestResponse:
    return await service.request_validation(session, payment_id, files)
