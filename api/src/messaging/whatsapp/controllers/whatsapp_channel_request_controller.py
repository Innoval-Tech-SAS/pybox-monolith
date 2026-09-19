import uuid
from typing import Annotated

from fastapi import Query

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from messaging.whatsapp.dependencies import WhatsAppChannelRequestServiceDep
from messaging.whatsapp.enums.whatsapp_enums import ChannelRequestStatus
from messaging.whatsapp.schemas.whatsapp_channel_request_schemas import (
    WhatsAppChannelRequestListResponse,
    WhatsAppChannelRequestResponse,
)

router = APIRouter(prefix="/whatsapp/channel-requests", tags=["Solicitudes de canal WhatsApp"])


@router.get("/", response_model=WhatsAppChannelRequestListResponse, summary="Listar solicitudes de canal WhatsApp")
async def list_whatsapp_channel_requests(
    session: CurrentSession,
    service: WhatsAppChannelRequestServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    request_status: Annotated[ChannelRequestStatus | None, Query(alias="status")] = None,
) -> WhatsAppChannelRequestListResponse:
    items, total = await service.list_by_org(organization_id, page, page_size, session, request_status)
    return WhatsAppChannelRequestListResponse(
        items=[WhatsAppChannelRequestResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch(
    "/{request_id}/approve",
    response_model=WhatsAppChannelRequestResponse,
    summary="Aprobar una solicitud de canal WhatsApp",
)
async def approve_whatsapp_channel_request(
    request_id: uuid.UUID,
    session: CurrentSession,
    service: WhatsAppChannelRequestServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> WhatsAppChannelRequestResponse:
    case = await service.approve(request_id, organization_id, session)
    return WhatsAppChannelRequestResponse.model_validate(case)


@router.patch(
    "/{request_id}/reject",
    response_model=WhatsAppChannelRequestResponse,
    summary="Rechazar una solicitud de canal WhatsApp",
)
async def reject_whatsapp_channel_request(
    request_id: uuid.UUID,
    session: CurrentSession,
    service: WhatsAppChannelRequestServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> WhatsAppChannelRequestResponse:
    case = await service.reject(request_id, organization_id, session)
    return WhatsAppChannelRequestResponse.model_validate(case)
