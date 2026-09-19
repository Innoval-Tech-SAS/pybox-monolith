import uuid
from datetime import datetime
from typing import Annotated

from fastapi import Query, status

from messaging.campaigns.constants.campaign_options import PERIODICITY_LABELS, WEEKDAYS
from messaging.campaigns.dependencies import CampaignServiceDep
from messaging.campaigns.enums.campaign_enums import Periodicity
from messaging.campaigns.schemas.campaign_schemas import (
    CampaignCreateRequest,
    CampaignListResponse,
    CampaignResponse,
    CampaignTimelineResponse,
    CampaignUpdateRequest,
)
from messaging.campaigns.services.automation_service import is_executing
from core.config.api_router import APIRouter
from core.security.constants.permissions import ORG_CAMPAIGNS
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_admin_or_org, require_global_admin

router = APIRouter(prefix="/campaigns", tags=["Campañas"])


@router.get("/periodicities", summary="Periodicidades disponibles para programar campañas")
async def list_periodicities(session: CurrentSession) -> list[dict]:
    return [{"value": p.value, "label": PERIODICITY_LABELS[p]} for p in Periodicity]


@router.get("/weekdays", summary="Días de la semana disponibles para campañas recurrentes")
async def list_weekdays(session: CurrentSession) -> list[dict]:
    return [{"value": value, "label": label, "active": active} for value, label, active in WEEKDAYS]


@router.get("/", response_model=CampaignListResponse, summary="Listar campañas del portafolio")
async def list_campaigns(
    session: CurrentSession,
    service: CampaignServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    search: Annotated[str | None, Query(description="Búsqueda por nombre de campaña")] = None,
    sort: Annotated[str, Query(description="Campo de orden: name | status")] = "name",
    sort_order: Annotated[str, Query(alias="sort_order", pattern="^(asc|desc)$")] = "asc",
) -> CampaignListResponse:
    campaigns, total, recipient_counts = await service.list_by_org(
        portfolio_id, page, page_size, session, search, sort, sort_order
    )
    return CampaignListResponse(
        items=[
            CampaignResponse.model_validate(c).model_copy(
                update={"total_recipients": recipient_counts[c.id]}
            )
            for c in campaigns
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/timeline",
    response_model=CampaignTimelineResponse,
    summary="Calendario de ejecuciones programadas de campañas",
)
async def campaigns_timeline(
    session: CurrentSession,
    service: CampaignServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
    range_start: Annotated[datetime, Query(alias="from")],
    range_end: Annotated[datetime, Query(alias="to")],
) -> CampaignTimelineResponse:
    require_admin_or_org(ORG_CAMPAIGNS, session, str(organization_id))
    items = await service.timeline(organization_id, range_start, range_end)
    return CampaignTimelineResponse(items=items, range_start=range_start, range_end=range_end)


@router.get("/{campaign_id}", response_model=CampaignResponse, summary="Obtener campaña por ID")
async def get_campaign(
    campaign_id: uuid.UUID,
    session: CurrentSession,
    service: CampaignServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> CampaignResponse:
    campaign = await service.get_by_id(campaign_id, portfolio_id, session)
    return CampaignResponse.model_validate(campaign)


@router.post(
    "/",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear campaña",
)
async def create_campaign(
    body: CampaignCreateRequest,
    session: CurrentSession,
    service: CampaignServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> CampaignResponse:
    campaign = await service.create(portfolio_id, body, session)
    return CampaignResponse.model_validate(campaign)


@router.patch("/{campaign_id}", response_model=CampaignResponse, summary="Actualizar campaña")
async def update_campaign(
    campaign_id: uuid.UUID,
    body: CampaignUpdateRequest,
    session: CurrentSession,
    service: CampaignServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> CampaignResponse:
    campaign = await service.update(campaign_id, portfolio_id, body, session)
    return CampaignResponse.model_validate(campaign)


@router.delete(
    "/{campaign_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar campaña (soft delete)",
)
async def delete_campaign(
    campaign_id: uuid.UUID,
    session: CurrentSession,
    service: CampaignServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> None:
    await service.delete(campaign_id, portfolio_id, session)


@router.post(
    "/{campaign_id}/restore",
    status_code=status.HTTP_200_OK,
    summary="Restaurar campaña",
    description="Solo administradores globales — restaurar no es un poder de admin de organización.",
)
async def restore_campaign(
    campaign_id: uuid.UUID,
    session: CurrentSession,
    service: CampaignServiceDep,
) -> CampaignResponse:
    require_global_admin(session)
    campaign = await service.restore(campaign_id)
    return CampaignResponse.model_validate(campaign)


@router.post("/{campaign_id}/activate", response_model=CampaignResponse, summary="Activar campaña")
async def activate_campaign(
    campaign_id: uuid.UUID,
    session: CurrentSession,
    service: CampaignServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> CampaignResponse:
    campaign = await service.activate(campaign_id, portfolio_id, session)
    return CampaignResponse.model_validate(campaign)


@router.get("/{campaign_id}/status", summary="Estado de ejecución de la campaña")
async def campaign_execution_status(
    campaign_id: uuid.UUID,
    session: CurrentSession,
    service: CampaignServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> dict:
    campaign = await service.get_by_id(campaign_id, portfolio_id, session)
    return {
        "campaign_id": campaign.id,
        "status": campaign.status,
        "is_executing": is_executing(campaign_id),
    }


@router.post("/{campaign_id}/pause", response_model=CampaignResponse, summary="Pausar campaña")
async def pause_campaign(
    campaign_id: uuid.UUID,
    session: CurrentSession,
    service: CampaignServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> CampaignResponse:
    campaign = await service.pause(campaign_id, portfolio_id, session)
    return CampaignResponse.model_validate(campaign)
