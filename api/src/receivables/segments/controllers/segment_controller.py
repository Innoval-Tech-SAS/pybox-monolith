import uuid
from typing import Annotated

from fastapi import Query, status

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_global_admin
from receivables.segments.dependencies import SegmentServiceDep
from receivables.segments.schemas.segment_schemas import (
    SegmentCreateRequest,
    SegmentExecuteRequest,
    SegmentExecuteResponse,
    SegmentExecutionResponse,
    SegmentListResponse,
    SegmentResponse,
    SegmentUpdateRequest,
)

router = APIRouter(prefix="/segments", tags=["Segmentos"])


@router.post(
    "/",
    response_model=SegmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear segmento",
)
async def create_segment(
    body: SegmentCreateRequest,
    session: CurrentSession,
    service: SegmentServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> SegmentResponse:
    segment = await service.create(portfolio_id, body, session)
    return SegmentResponse.model_validate(segment)


@router.get(
    "/", response_model=SegmentListResponse, summary="Listar segmentos del portafolio"
)
async def list_segments(
    session: CurrentSession,
    service: SegmentServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
) -> SegmentListResponse:
    segments, total = await service.list_by_org(portfolio_id, page, page_size, session)
    return SegmentListResponse(
        items=[SegmentResponse.model_validate(s) for s in segments],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/options",
    response_model=list[SegmentResponse],
    summary="Listar todos los segmentos del portafolio sin paginar (uso en selects)",
)
async def list_segment_options(
    session: CurrentSession,
    service: SegmentServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> list[SegmentResponse]:
    return await service.list_all_by_org(portfolio_id, session)


@router.get(
    "/{segment_id}", response_model=SegmentResponse, summary="Obtener segmento por ID"
)
async def get_segment(
    segment_id: uuid.UUID,
    session: CurrentSession,
    service: SegmentServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> SegmentResponse:
    segment = await service.get(segment_id, portfolio_id, session)
    return SegmentResponse.model_validate(segment)


@router.patch(
    "/{segment_id}", response_model=SegmentResponse, summary="Actualizar segmento"
)
async def update_segment(
    segment_id: uuid.UUID,
    body: SegmentUpdateRequest,
    session: CurrentSession,
    service: SegmentServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> SegmentResponse:
    segment = await service.update(segment_id, portfolio_id, body, session)
    return SegmentResponse.model_validate(segment)


@router.delete(
    "/{segment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar segmento"
)
async def delete_segment(
    segment_id: uuid.UUID,
    session: CurrentSession,
    service: SegmentServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> None:
    await service.delete(segment_id, portfolio_id, session)


@router.post(
    "/{segment_id}/restore",
    status_code=status.HTTP_200_OK,
    response_model=SegmentResponse,
    summary="Restaurar segmento",
    description="Solo administradores globales.",
)
async def restore_segment(
    segment_id: uuid.UUID,
    session: CurrentSession,
    service: SegmentServiceDep,
):
    require_global_admin(session)
    segment = await service.restore(segment_id)
    return SegmentResponse.model_validate(segment)


@router.post(
    "/{segment_id}/execute",
    response_model=SegmentExecuteResponse,
    summary="Ejecutar segmento",
)
async def execute_segment(
    segment_id: uuid.UUID,
    body: SegmentExecuteRequest,
    session: CurrentSession,
    service: SegmentServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> SegmentExecuteResponse:
    result = await service.execute(
        segment_id, portfolio_id, body, session.user_id, session
    )
    return SegmentExecuteResponse(**result)


@router.get(
    "/{segment_id}/executions",
    response_model=list[SegmentExecutionResponse],
    summary="Listar ejecuciones de un segmento",
)
async def list_executions(
    segment_id: uuid.UUID,
    session: CurrentSession,
    service: SegmentServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> list[SegmentExecutionResponse]:
    executions = await service.list_executions(segment_id, portfolio_id, session)
    return [SegmentExecutionResponse.model_validate(e) for e in executions]
