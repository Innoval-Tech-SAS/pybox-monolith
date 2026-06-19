import uuid
from typing import Annotated

from fastapi import Query, status

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from core.security.permissions import ORG_TEMPLATES
from core.security.policies import require_admin_or_org
from messaging.templates.dependencies import TemplateServiceDep, TemplateVariableServiceDep
from messaging.templates.enums.template_enums import TemplateChannel
from messaging.templates.schemas.template_schemas import (
    TemplateCreateRequest,
    TemplateListResponse,
    TemplatePreviewRequest,
    TemplatePreviewResponse,
    TemplateResponse,
    TemplateUpdateRequest,
    TemplateVariableOption,
)

router = APIRouter(prefix="/templates", tags=["Plantillas"])


@router.get("/", response_model=TemplateListResponse, summary="Listar plantillas de la organización")
async def list_templates(
    session: CurrentSession,
    service: TemplateServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    channel: Annotated[TemplateChannel | None, Query(alias="channel")] = None,
) -> TemplateListResponse:
    require_admin_or_org(ORG_TEMPLATES, session, str(organization_id))
    templates, total = await service.list_by_org(organization_id, page, page_size, channel)
    return TemplateListResponse(
        items=[TemplateResponse.model_validate(t) for t in templates],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/variables",
    response_model=list[TemplateVariableOption],
    summary="Listar variables disponibles para construir el contenido de una plantilla",
)
async def list_template_variables(
    session: CurrentSession,
    service: TemplateVariableServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> list[TemplateVariableOption]:
    require_admin_or_org(ORG_TEMPLATES, session, str(organization_id))
    return await service.list_available_variables()


@router.get(
    "/options",
    response_model=list[TemplateResponse],
    summary="Listar todas las plantillas de la organización sin paginar (uso en selects)",
)
async def list_template_options(
    session: CurrentSession,
    service: TemplateServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
    channel: Annotated[TemplateChannel | None, Query(alias="channel")] = None,
) -> list[TemplateResponse]:
    require_admin_or_org(ORG_TEMPLATES, session, str(organization_id))
    templates = await service.list_all_by_org(organization_id, channel)
    return [TemplateResponse.model_validate(t) for t in templates]


@router.get("/{template_id}", response_model=TemplateResponse, summary="Obtener plantilla por ID")
async def get_template(
    template_id: uuid.UUID,
    session: CurrentSession,
    service: TemplateServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> TemplateResponse:
    require_admin_or_org(ORG_TEMPLATES, session, str(organization_id))
    template = await service.get_by_id(template_id, organization_id)
    return TemplateResponse.model_validate(template)


@router.post(
    "/",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear plantilla",
)
async def create_template(
    body: TemplateCreateRequest,
    session: CurrentSession,
    service: TemplateServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> TemplateResponse:
    require_admin_or_org(ORG_TEMPLATES, session, str(organization_id))
    template = await service.create(organization_id, body)
    return TemplateResponse.model_validate(template)


@router.patch("/{template_id}", response_model=TemplateResponse, summary="Actualizar plantilla")
async def update_template(
    template_id: uuid.UUID,
    body: TemplateUpdateRequest,
    session: CurrentSession,
    service: TemplateServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> TemplateResponse:
    require_admin_or_org(ORG_TEMPLATES, session, str(organization_id))
    template = await service.update(template_id, organization_id, body)
    return TemplateResponse.model_validate(template)


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar plantilla (soft delete)",
)
async def delete_template(
    template_id: uuid.UUID,
    session: CurrentSession,
    service: TemplateServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> None:
    require_admin_or_org(ORG_TEMPLATES, session, str(organization_id))
    await service.delete(template_id, organization_id)


@router.post(
    "/{template_id}/preview",
    response_model=TemplatePreviewResponse,
    summary="Previsualizar plantilla renderizada con variables de prueba",
)
async def preview_template(
    template_id: uuid.UUID,
    body: TemplatePreviewRequest,
    session: CurrentSession,
    service: TemplateServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> TemplatePreviewResponse:
    require_admin_or_org(ORG_TEMPLATES, session, str(organization_id))
    return await service.preview(template_id, organization_id, body)

