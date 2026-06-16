import uuid
from typing import Annotated

from fastapi import Query

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from core.security.policies import require_permission
from core.security.permissions import ORG_CAMPAIGNS
from messaging.contacts.dependencies import ContactServiceDep
from messaging.contacts.schemas.contact_schemas import ContactsByChannelGroup

router = APIRouter(prefix="/contacts", tags=["Contactos"])


@router.get(
    "/debtor/{debtor_id}",
    response_model=list[ContactsByChannelGroup],
    summary="Historial de contactos de un deudor agrupado por canal",
)
async def get_debtor_contacts(
    debtor_id: int,
    session: CurrentSession,
    service: ContactServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
    portfolio_id: Annotated[uuid.UUID | None, Query(alias="portfolioId")] = None,
) -> list[ContactsByChannelGroup]:
    require_permission(ORG_CAMPAIGNS, session, str(organization_id))
    return await service.get_by_debtor(debtor_id, organization_id, portfolio_id)
