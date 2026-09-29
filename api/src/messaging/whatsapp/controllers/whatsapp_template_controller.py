import uuid
from typing import Annotated

from fastapi import Query, status

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_global_admin
from messaging.templates.schemas.template_schemas import TemplateResponse
from messaging.whatsapp.dependencies import WhatsAppTemplateServiceDep
from messaging.whatsapp.schemas.whatsapp_template_data_schemas import (
    WhatsAppTemplateCreateRequest,
    WhatsAppTemplateDataResponse,
    WhatsAppTemplateListResponse,
    WhatsAppTemplateResponse,
    WhatsAppTemplateVariableSlotResponse,
)

router = APIRouter(prefix="/whatsapp/templates", tags=["Plantillas de WhatsApp"])


@router.post(
    "/",
    response_model=WhatsAppTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear plantilla de WhatsApp (se registra en Meta)",
)
async def create_whatsapp_template(
    body: WhatsAppTemplateCreateRequest,
    session: CurrentSession,
    service: WhatsAppTemplateServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> WhatsAppTemplateResponse:
    template, whatsapp_data = await service.create(portfolio_id, body, session)
    return WhatsAppTemplateResponse(
        template=TemplateResponse.model_validate(template),
        whatsapp=WhatsAppTemplateDataResponse.model_validate(whatsapp_data),
    )


@router.get(
    "/",
    response_model=WhatsAppTemplateListResponse,
    summary="Listar plantillas de WhatsApp del portafolio",
)
async def list_whatsapp_templates(
    session: CurrentSession,
    service: WhatsAppTemplateServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
) -> WhatsAppTemplateListResponse:
    rows, total = await service.list_by_org(portfolio_id, page, page_size, session)
    return WhatsAppTemplateListResponse(
        items=[
            WhatsAppTemplateResponse(
                template=TemplateResponse.model_validate(template),
                whatsapp=WhatsAppTemplateDataResponse.model_validate(whatsapp_data),
            )
            for template, whatsapp_data in rows
            if whatsapp_data is not None
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/{template_id}/refresh-status",
    response_model=WhatsAppTemplateResponse,
    summary="Refrescar el estado de aprobación de la plantilla consultando Meta",
)
async def refresh_whatsapp_template_status(
    template_id: uuid.UUID,
    session: CurrentSession,
    service: WhatsAppTemplateServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> WhatsAppTemplateResponse:
    template, whatsapp_data = await service.refresh_status(
        template_id, portfolio_id, session
    )
    return WhatsAppTemplateResponse(
        template=TemplateResponse.model_validate(template),
        whatsapp=WhatsAppTemplateDataResponse.model_validate(whatsapp_data),
    )


@router.get(
    "/{template_id}/variables",
    response_model=list[WhatsAppTemplateVariableSlotResponse],
    summary="Listar variables de la plantilla, consultadas en vivo a Meta",
)
async def list_whatsapp_template_variables(
    template_id: uuid.UUID,
    session: CurrentSession,
    service: WhatsAppTemplateServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> list[WhatsAppTemplateVariableSlotResponse]:
    return await service.list_variables(template_id, portfolio_id, session)


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar plantilla de WhatsApp (en Meta y localmente)",
)
async def delete_whatsapp_template(
    template_id: uuid.UUID,
    session: CurrentSession,
    service: WhatsAppTemplateServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> None:
    await service.delete(template_id, portfolio_id, session)


@router.post(
    "/{template_id}/restore",
    status_code=status.HTTP_200_OK,
    summary="Restaurar plantilla de WhatsApp (solo localmente)",
    description="Solo administradores globales. El borrado en Meta es irreversible: "
    "esto solo restaura las filas locales, la plantilla no vuelve a existir en Meta "
    "hasta que se resubmita.",
)
async def restore_whatsapp_template(
    template_id: uuid.UUID,
    session: CurrentSession,
    service: WhatsAppTemplateServiceDep,
) -> TemplateResponse:
    require_global_admin(session)
    template = await service.restore(template_id)
    return TemplateResponse.model_validate(template)
