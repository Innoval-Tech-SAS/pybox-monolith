import uuid
from typing import Annotated

from fastapi import Query, status

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from core.security.policies import require_org_access
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


@router.post("/", response_model=SegmentResponse, status_code=status.HTTP_201_CREATED, summary="Crear segmento")
async def create_segment(
    body: SegmentCreateRequest,
    session: CurrentSession,
    service: SegmentServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> SegmentResponse:
    require_org_access(session, str(organization_id))
    segment = await service.create(organization_id, body)
    return SegmentResponse.model_validate(segment)


@router.get("/", response_model=SegmentListResponse, summary="Listar segmentos de la organización")
async def list_segments(
    session: CurrentSession,
    service: SegmentServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
) -> SegmentListResponse:
    require_org_access(session, str(organization_id))
    segments, total = await service.list_by_org(organization_id, page, page_size)
    return SegmentListResponse(
        items=[SegmentResponse.model_validate(s) for s in segments],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/options",
    response_model=list[SegmentResponse],
    summary="Listar todos los segmentos de la organización sin paginar (uso en selects)",
)
async def list_segment_options(
    session: CurrentSession,
    service: SegmentServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> list[SegmentResponse]:
    require_org_access(session, str(organization_id))
    segments = await service.list_all_by_org(organization_id)
    return [SegmentResponse.model_validate(s) for s in segments]


@router.get("/{segment_id}", response_model=SegmentResponse, summary="Obtener segmento por ID")
async def get_segment(
    segment_id: uuid.UUID,
    session: CurrentSession,
    service: SegmentServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> SegmentResponse:
    require_org_access(session, str(organization_id))
    segment = await service.get(segment_id, organization_id)
    return SegmentResponse.model_validate(segment)


@router.patch("/{segment_id}", response_model=SegmentResponse, summary="Actualizar segmento")
async def update_segment(
    segment_id: uuid.UUID,
    body: SegmentUpdateRequest,
    session: CurrentSession,
    service: SegmentServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> SegmentResponse:
    require_org_access(session, str(organization_id))
    segment = await service.update(segment_id, organization_id, body)
    return SegmentResponse.model_validate(segment)


@router.delete("/{segment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar segmento")
async def delete_segment(
    segment_id: uuid.UUID,
    session: CurrentSession,
    service: SegmentServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> None:
    require_org_access(session, str(organization_id))
    await service.delete(segment_id, organization_id)


@router.post("/{segment_id}/execute", response_model=SegmentExecuteResponse, summary="Ejecutar segmento")
async def execute_segment(
    segment_id: uuid.UUID,
    body: SegmentExecuteRequest,
    session: CurrentSession,
    service: SegmentServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> SegmentExecuteResponse:
    require_org_access(session, str(organization_id))
    result = await service.execute(segment_id, organization_id, body, session.user_id)
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
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> list[SegmentExecutionResponse]:
    require_org_access(session, str(organization_id))
    executions = await service.list_executions(segment_id, organization_id)
    return [SegmentExecutionResponse.model_validate(e) for e in executions]
