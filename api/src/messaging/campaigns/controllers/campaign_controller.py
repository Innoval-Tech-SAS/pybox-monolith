import uuid
from typing import Annotated

from fastapi import Query, status

from messaging.campaigns.dependencies import CampaignServiceDep
from messaging.campaigns.schemas.campaign_schemas import (
    CampaignCreateRequest,
    CampaignResponse,
    CampaignUpdateRequest,
)
from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from core.security.permissions import ORG_CAMPAIGNS
from core.security.policies import require_org_admin, require_permission

router = APIRouter(prefix="/campaigns", tags=["Campañas"])


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
