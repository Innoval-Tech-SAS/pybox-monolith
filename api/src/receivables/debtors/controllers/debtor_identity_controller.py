from fastapi import Depends

from core.config.api_router import APIRouter
from core.security.dependencies import require_n8n_service_key
from receivables.debtors.dependencies import DebtorIdentityServiceDep
from receivables.debtors.schemas.debtor_identity_schemas import (
    IdentityChallengeRequest,
    IdentityChallengeResponse,
    IdentityVerifyRequest,
    IdentityVerifyResponse,
)

# Solo lo consume n8n, autenticado con la llave de servicio (sin sesión de usuario). No se
# publica en el esquema OpenAPI, igual que los webhooks.
router = APIRouter(
    prefix="/internal/debtor-identity",
    tags=["Identidad del deudor (interno)"],
    dependencies=[Depends(require_n8n_service_key)],
    include_in_schema=False,
)


@router.post(
    "/challenge",
    response_model=IdentityChallengeResponse,
    summary="Dato con el que el titular debe confirmar su identidad",
)
async def request_challenge(
    data: IdentityChallengeRequest, service: DebtorIdentityServiceDep
) -> IdentityChallengeResponse:
    return await service.request_challenge(data)


@router.post(
    "/verify",
    response_model=IdentityVerifyResponse,
    summary="Verifica el dato que escribió el titular",
)
async def verify(data: IdentityVerifyRequest, service: DebtorIdentityServiceDep) -> IdentityVerifyResponse:
    return await service.verify(data)
