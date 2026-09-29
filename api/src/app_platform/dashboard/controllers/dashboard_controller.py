import uuid
from typing import Annotated

from fastapi import Query

from app_platform.dashboard.dependencies import DashboardServiceDep
from app_platform.dashboard.schemas.dashboard_schemas import (
    DashboardCampaignOption,
    MonthlySendsResponse,
    OrganizationStatsResponse,
    SendStatusCountsResponse,
)
from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_org_admin

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

OrganizationIdQuery = Annotated[uuid.UUID, Query(alias="organizationId")]


@router.get(
    "/organization-stats",
    response_model=OrganizationStatsResponse,
    summary=(
        "Estadísticas agregadas de portafolios, créditos y deudores de la organización"
    ),
)
async def get_organization_stats(
    session: CurrentSession,
    service: DashboardServiceDep,
    organization_id: OrganizationIdQuery,
) -> OrganizationStatsResponse:
    require_org_admin(session, str(organization_id))
    return await service.get_organization_stats(organization_id)


@router.get(
    "/campaigns",
    response_model=list[DashboardCampaignOption],
    summary="Listar campañas de la organización para el filtro de envíos mensuales",
)
async def list_campaign_options(
    session: CurrentSession,
    service: DashboardServiceDep,
    organization_id: OrganizationIdQuery,
) -> list[DashboardCampaignOption]:
    require_org_admin(session, str(organization_id))
    return await service.list_campaign_options(organization_id)


@router.get(
    "/send-status-counts",
    response_model=SendStatusCountsResponse,
    summary="Conteo de contactos por status de envío en la organización",
)
async def get_send_status_counts(
    session: CurrentSession,
    service: DashboardServiceDep,
    organization_id: OrganizationIdQuery,
) -> SendStatusCountsResponse:
    require_org_admin(session, str(organization_id))
    return await service.get_send_status_counts(organization_id)


@router.get(
    "/monthly-sends",
    response_model=MonthlySendsResponse,
    summary="Envíos mensuales de una campaña en los últimos 12 meses",
)
async def get_monthly_sends(
    session: CurrentSession,
    service: DashboardServiceDep,
    organization_id: OrganizationIdQuery,
    campaign_id: Annotated[uuid.UUID, Query(alias="campaignId")],
) -> MonthlySendsResponse:
    require_org_admin(session, str(organization_id))
    return await service.get_monthly_sends(organization_id, campaign_id)
