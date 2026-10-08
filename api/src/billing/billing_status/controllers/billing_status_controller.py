"""Endpoint de consulta del estado de bloqueo por facturación de una organización."""

import uuid
from typing import Annotated

from fastapi import Query

from billing.billing_status.dependencies import BillingStatusServiceDep
from billing.billing_status.schemas.billing_status_schemas import (
    TenantBillingStatusResponse,
)
from core.config.api_router import APIRouter
from core.security.constants.permissions import ORG_BILLING
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_permission

router = APIRouter(prefix="/billing", tags=["Facturación"])


@router.get(
    "/status",
    response_model=TenantBillingStatusResponse,
    summary="Obtener estado de bloqueo por facturación",
)
async def get_tenant_billing_status(
    session: CurrentSession,
    service: BillingStatusServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> TenantBillingStatusResponse:
    require_permission(ORG_BILLING, session, str(organization_id))
    return await service.get_status(organization_id)
