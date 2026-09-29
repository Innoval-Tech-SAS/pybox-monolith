import uuid
from typing import Annotated

from fastapi import Query, Response

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from receivables.statements.dependencies import StatementServiceDep
from receivables.statements.schemas.statement_schemas import (
    GenerateStatementRequest,
    StatementListResponse,
    StatementResponse,
)

router = APIRouter(prefix="/debtors/{debtor_id}/statements", tags=["Extractos"])


@router.post(
    "",
    response_model=StatementResponse,
    summary="Generar extracto de un deudor",
    description=(
        "Genera un PDF con el estado de cuenta del deudor al momento de la "
        "solicitud. Sin `creditId` en el body: consolidado con todos los "
        "créditos activos del deudor en el portafolio. Con `creditId`: extracto "
        "de ese crédito puntual."
    ),
)
async def generate_statement(
    debtor_id: uuid.UUID,
    body: GenerateStatementRequest,
    session: CurrentSession,
    service: StatementServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> StatementResponse:
    return await service.generate(debtor_id, portfolio_id, body.credit_id, session)


@router.get(
    "",
    response_model=StatementListResponse,
    summary="Listar extractos de un deudor",
    description=(
        "Extractos generados para el deudor en el portafolio dado, del más "
        "reciente al más antiguo."
    ),
)
async def list_statements(
    debtor_id: uuid.UUID,
    session: CurrentSession,
    service: StatementServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> StatementListResponse:
    return await service.list_for_org(debtor_id, portfolio_id, session)


@router.get(
    "/{statement_id}/content",
    summary="Descargar un extracto",
    description="Autoriza contra el portafolio y entrega el archivo desde el almacén.",
    response_class=Response,
)
async def download_statement(
    debtor_id: uuid.UUID,
    statement_id: uuid.UUID,
    session: CurrentSession,
    service: StatementServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> Response:
    return await service.get_content_for_org(
        statement_id, debtor_id, portfolio_id, session
    )
