"""Endpoint de autogestión: solicitud de liquidación (settlement) de un crédito."""

import uuid
from typing import Annotated

from fastapi import File, UploadFile, status

from core.config.api_router import APIRouter
from receivables.credits.dependencies import CreditSelfServiceServiceDep, RequireSelf
from receivables.credits.schemas.credit_selfservice_schemas import (
    SettlementRequestResponse,
)

router = APIRouter(prefix="/credits", tags=["Autogestión de créditos"])


@router.post(
    "/{credit_id}/settlement",
    response_model=SettlementRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar la baja de un crédito adjuntando comprobante",
    description=(
        "El titular (USER/SELF) pide dar de baja un crédito propio. Crea un "
        "ticket hacia la organización dueña; al aprobarlo se registra el pago "
        "total y el crédito se desactiva."
    ),
)
async def request_settlement(
    credit_id: uuid.UUID,
    files: Annotated[list[UploadFile], File()],
    session: RequireSelf,
    service: CreditSelfServiceServiceDep,
) -> SettlementRequestResponse:
    return await service.request_settlement(session, credit_id, files)
