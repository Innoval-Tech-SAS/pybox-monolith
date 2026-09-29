import uuid

from fastapi import Response

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from receivables.statements.dependencies import StatementServiceDep
from receivables.statements.schemas.statement_schemas import StatementListResponse

router = APIRouter(prefix="/statements", tags=["Mis Extractos"])


@router.get(
    "/my-statements",
    response_model=StatementListResponse,
    summary="Consultar mis extractos",
    description=(
        "Extractos del titular autenticado, generados por cualquier "
        "organización acreedora."
    ),
)
async def list_my_statements(
    session: CurrentSession,
    service: StatementServiceDep,
) -> StatementListResponse:
    return await service.list_mine(session)


@router.get(
    "/my-statements/{statement_id}/content",
    summary="Descargar uno de mis extractos",
    description=(
        "Autoriza contra el titular de la sesión y entrega el archivo desde el almacén."
    ),
    response_class=Response,
)
async def download_my_statement(
    statement_id: uuid.UUID,
    session: CurrentSession,
    service: StatementServiceDep,
) -> Response:
    return await service.get_content_mine(statement_id, session)
