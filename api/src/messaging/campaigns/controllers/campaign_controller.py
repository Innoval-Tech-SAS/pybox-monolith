import uuid
from typing import Annotated

from fastapi import Query, status

from messaging.campaigns.constants.campaign_options import PERIODICITY_LABELS, WEEKDAYS
from messaging.campaigns.dependencies import CampaignServiceDep
from messaging.campaigns.enums.campaign_enums import Periodicity
from messaging.campaigns.schemas.campaign_schemas import (
    CampaignCreateRequest,
    CampaignResponse,
    CampaignUpdateRequest,
)
from messaging.campaigns.services.automation_service import is_executing
from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from core.security.permissions import ORG_CAMPAIGNS
from core.security.policies import require_org_admin, require_permission

router = APIRouter(prefix="/campaigns", tags=["Campañas"])


@router.get("/periodicities", summary="Periodicidades disponibles para programar campañas")
async def list_periodicities(
    session: CurrentSession,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> list[dict]:
    require_permission(ORG_CAMPAIGNS, session, str(organization_id))
    return [{"value": p.value, "label": PERIODICITY_LABELS[p]} for p in Periodicity]


@router.get("/weekdays", summary="Días de la semana disponibles para campañas recurrentes")
async def list_weekdays(
    session: CurrentSession,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> list[dict]:
    require_permission(ORG_CAMPAIGNS, session, str(organization_id))
    return [{"value": value, "label": label, "active": active} for value, label, active in WEEKDAYS]


@router.get("/", response_model=list[CampaignResponse], summary="Listar campañas de la organización")
async def list_campaigns(
    session: CurrentSession,
    service: CampaignServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> list[CampaignResponse]:
    require_permission(ORG_CAMPAIGNS, session, str(organization_id))
    campaigns = await service.list_by_org(organization_id)
    return [CampaignResponse.model_validate(c) for c in campaigns]


@router.get("/{campaign_id}", response_model=CampaignResponse, summary="Obtener campaña por ID")
async def get_campaign(
    campaign_id: uuid.UUID,
    session: CurrentSession,
    service: CampaignServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> CampaignResponse:
    require_permission(ORG_CAMPAIGNS, session, str(organization_id))
    campaign = await service.get_by_id(campaign_id, organization_id)
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
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> CampaignResponse:
    require_org_admin(session, str(organization_id))
    campaign = await service.create(organization_id, body)
    return CampaignResponse.model_validate(campaign)


@router.patch("/{campaign_id}", response_model=CampaignResponse, summary="Actualizar campaña")
async def update_campaign(
    campaign_id: uuid.UUID,
    body: CampaignUpdateRequest,
    session: CurrentSession,
    service: CampaignServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> CampaignResponse:
    require_org_admin(session, str(organization_id))
    campaign = await service.update(campaign_id, organization_id, body)
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
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> None:
    require_org_admin(session, str(organization_id))
    await service.delete(campaign_id, organization_id)


@router.post("/{campaign_id}/activate", response_model=CampaignResponse, summary="Activar campaña")
async def activate_campaign(
    campaign_id: uuid.UUID,
    session: CurrentSession,
    service: CampaignServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> CampaignResponse:
    require_org_admin(session, str(organization_id))
    campaign = await service.activate(campaign_id, organization_id)
    return CampaignResponse.model_validate(campaign)


@router.get("/{campaign_id}/status", summary="Estado de ejecución de la campaña")
async def campaign_execution_status(
    campaign_id: uuid.UUID,
    session: CurrentSession,
    service: CampaignServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> dict:
    require_permission(ORG_CAMPAIGNS, session, str(organization_id))
    campaign = await service.get_by_id(campaign_id, organization_id)
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
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> CampaignResponse:
    require_org_admin(session, str(organization_id))
    campaign = await service.pause(campaign_id, organization_id)
    return CampaignResponse.model_validate(campaign)
