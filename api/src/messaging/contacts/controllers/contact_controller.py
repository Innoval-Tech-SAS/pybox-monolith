import uuid
from typing import Annotated

from fastapi import Query

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from messaging.contacts.dependencies import ContactServiceDep
from messaging.contacts.schemas.contact_schemas import ContactsByChannelGroup

router = APIRouter(prefix="/contacts", tags=["Contactos"])


@router.get(
    "/debtor/{debtor_id}",
    response_model=list[ContactsByChannelGroup],
    summary="Historial de envíos de un deudor agrupado por canal",
)
async def get_debtor_contacts(
    debtor_id: uuid.UUID,
    session: CurrentSession,
    service: ContactServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
) -> list[ContactsByChannelGroup]:
    return await service.get_by_debtor(
        debtor_id, portfolio_id, session, page, page_size
    )
