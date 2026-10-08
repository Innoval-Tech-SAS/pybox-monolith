"""Endpoint de reporte de campaña IVR (resumen exportable)."""

import uuid
from typing import Annotated

from fastapi import Query
from fastapi.responses import Response

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from messaging.ivr.dependencies import IvrMonitorServiceDep, IvrReportServiceDep
from messaging.ivr.schemas.ivr_report_schemas import IvrCampaignReportSchema

router = APIRouter(prefix="/ivr/reports", tags=["IVR - Reportes"])


@router.get(
    "/campaign/{campaign_id}",
    response_model=IvrCampaignReportSchema,
    summary="Reporte de resultados de una campaña IVR",
)
async def get_campaign_report(
    campaign_id: uuid.UUID,
    session: CurrentSession,
    monitor: IvrMonitorServiceDep,
    service: IvrReportServiceDep,
) -> IvrCampaignReportSchema:
    # El monitor ya resuelve campaña -> portafolio -> organización; se reutiliza
    # para no duplicar la política de acceso.
    await monitor.authorize_campaign(campaign_id, session)
    return await service.build(campaign_id)


@router.get(
    "/campaign/{campaign_id}/export",
    summary="Exportar las llamadas de una campaña IVR en CSV",
    response_class=Response,
)
async def export_campaign_calls(
    campaign_id: uuid.UUID,
    session: CurrentSession,
    monitor: IvrMonitorServiceDep,
    service: IvrReportServiceDep,
    filename: Annotated[str | None, Query()] = None,
) -> Response:
    await monitor.authorize_campaign(campaign_id, session)
    csv_text = await service.export_csv(campaign_id)

    safe_name = (filename or f"llamadas_{campaign_id}").replace('"', "")
    return Response(
        # BOM para que Excel en Windows abra el CSV en UTF-8 sin romper acentos.
        content="﻿" + csv_text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}.csv"'},
    )
