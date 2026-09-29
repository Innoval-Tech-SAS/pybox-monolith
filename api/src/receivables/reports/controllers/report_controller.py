"""Endpoints de reportes de cartera: alta, edición y ejecución dinámica."""

import uuid
from typing import Annotated

from fastapi import BackgroundTasks, Depends, Query, status
from fastapi.responses import JSONResponse

from core.config.api_router import APIRouter
from core.security.constants.permissions import ORG_REPORTS
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import (
    require_admin_or_org,
    require_global_admin,
)
from core.security.rate_limit import rate_limit
from receivables.reports.background_tasks import execute_and_notify
from receivables.reports.dependencies import ReportServiceDep
from receivables.reports.schemas.report_schemas import (
    ReportCreateRequest,
    ReportExecuteRequest,
    ReportExecuteResponse,
    ReportExecutionResponse,
    ReportJobAccepted,
    ReportListResponse,
    ReportResponse,
    ReportUpdateRequest,
)

router = APIRouter(prefix="/reports", tags=["Reportes"])

_report_rate_limit = Depends(
    rate_limit("report-execute", max_attempts=30, window_seconds=60)
)


@router.post(
    "/",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear reporte",
)
async def create_report(
    body: ReportCreateRequest,
    session: CurrentSession,
    service: ReportServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> ReportResponse:
    require_admin_or_org(ORG_REPORTS, session, str(organization_id))
    report = await service.create(organization_id, body)
    return ReportResponse.model_validate(report)


@router.get(
    "/", response_model=ReportListResponse, summary="Listar reportes de la organización"
)
async def list_reports(
    session: CurrentSession,
    service: ReportServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
) -> ReportListResponse:
    require_admin_or_org(ORG_REPORTS, session, str(organization_id))
    reports, total = await service.list_by_org(organization_id, page, page_size)
    return ReportListResponse(
        items=[ReportResponse.model_validate(r) for r in reports],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{report_id}", response_model=ReportResponse, summary="Obtener reporte por ID"
)
async def get_report(
    report_id: uuid.UUID,
    session: CurrentSession,
    service: ReportServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> ReportResponse:
    require_admin_or_org(ORG_REPORTS, session, str(organization_id))
    report = await service.get(report_id, organization_id)
    return ReportResponse.model_validate(report)


@router.patch(
    "/{report_id}", response_model=ReportResponse, summary="Actualizar reporte"
)
async def update_report(
    report_id: uuid.UUID,
    body: ReportUpdateRequest,
    session: CurrentSession,
    service: ReportServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> ReportResponse:
    require_admin_or_org(ORG_REPORTS, session, str(organization_id))
    report = await service.update(report_id, organization_id, body)
    return ReportResponse.model_validate(report)


@router.delete(
    "/{report_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar reporte"
)
async def delete_report(
    report_id: uuid.UUID,
    session: CurrentSession,
    service: ReportServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> None:
    require_admin_or_org(ORG_REPORTS, session, str(organization_id))
    await service.delete(report_id, organization_id)


@router.post(
    "/{report_id}/restore",
    status_code=status.HTTP_200_OK,
    response_model=ReportResponse,
    summary="Restaurar reporte",
    description="Solo administradores globales.",
)
async def restore_report(
    report_id: uuid.UUID,
    session: CurrentSession,
    service: ReportServiceDep,
):
    require_global_admin(session)
    report = await service.restore(report_id)
    return ReportResponse.model_validate(report)


@router.post(
    "/{report_id}/execute",
    summary="Ejecutar reporte",
    dependencies=[_report_rate_limit],
    response_model=None,
    responses={
        200: {
            "model": ReportExecuteResponse,
            "description": "Resultado inmediato (modo preview)",
        },
        202: {
            "model": ReportJobAccepted,
            "description": "Reporte en proceso, notificación vía SSE (modo audit)",
        },
    },
)
async def execute_report(
    report_id: uuid.UUID,
    body: ReportExecuteRequest,
    background_tasks: BackgroundTasks,
    session: CurrentSession,
    service: ReportServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> ReportExecuteResponse | JSONResponse:
    require_admin_or_org(ORG_REPORTS, session, str(organization_id))

    if body.mode == "audit":
        background_tasks.add_task(
            execute_and_notify,
            report_id=report_id,
            organization_id=organization_id,
            request=body,
            user_id=session.user_id,
        )
        accepted = ReportJobAccepted(
            message=(
                "El reporte se está generando. Recibirás una notificación "
                "cuando esté listo."
            ),
            report_id=report_id,
            mode=body.mode,
        )
        return JSONResponse(
            content=accepted.model_dump(mode="json", by_alias=True),
            status_code=status.HTTP_202_ACCEPTED,
        )

    result = await service.execute(report_id, organization_id, body, session.user_id)
    return ReportExecuteResponse(**result)


@router.get(
    "/{report_id}/executions",
    response_model=list[ReportExecutionResponse],
    summary="Listar ejecuciones de un reporte",
)
async def list_executions(
    report_id: uuid.UUID,
    session: CurrentSession,
    service: ReportServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> list[ReportExecutionResponse]:
    require_admin_or_org(ORG_REPORTS, session, str(organization_id))
    executions = await service.list_executions(report_id, organization_id)
    return [ReportExecutionResponse.model_validate(e) for e in executions]
