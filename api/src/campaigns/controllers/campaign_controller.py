import uuid
from typing import Annotated

from fastapi import HTTPException, Query, status

from campaigns.dependencies import CampaignServiceDep
from campaigns.schemas.campaign_schemas import (
    CampaignCreateRequest,
    CampaignResponse,
    CampaignUpdateRequest,
)
from config.api_router import APIRouter
from security.dependencies import CurrentSession
from security.permissions import ORG_CAMPAIGNS
from security.policies import require_permission
from users.enums.user_enums import UserRole
from users.schemas.user_session_schema import UserSession

router = APIRouter(prefix="/campaigns", tags=["Campañas"])


def _require_admin(session: UserSession, org_id: str) -> None:
    if session.is_global:
        return
    org_entry = session.orgs.get(org_id)
    if org_entry is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin acceso a esta organización")
    if org_entry.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo administradores pueden realizar esta acción")


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
    _require_admin(session, str(organization_id))
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
    _require_admin(session, str(organization_id))
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
    _require_admin(session, str(organization_id))
    await service.delete(campaign_id, organization_id)
