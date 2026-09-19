import uuid
from typing import Annotated

from fastapi import Query

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from messaging.whatsapp.dependencies import WhatsAppErrorServiceDep
from messaging.whatsapp.schemas.whatsapp_error_schemas import WhatsAppSendErrorListResponse, WhatsAppSendErrorResponse

router = APIRouter(prefix="/whatsapp/errors", tags=["Errores de envío de WhatsApp"])


@router.get("/", response_model=WhatsAppSendErrorListResponse, summary="Listar errores de envío de WhatsApp")
async def list_whatsapp_send_errors(
    session: CurrentSession,
    service: WhatsAppErrorServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
) -> WhatsAppSendErrorListResponse:
    items, total = await service.list_by_org(organization_id, page, page_size, session)
    return WhatsAppSendErrorListResponse(
        items=[WhatsAppSendErrorResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
