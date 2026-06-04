import uuid
from typing import Annotated

from fastapi import HTTPException, Query, status

from config.api_router import APIRouter
from security.dependencies import CurrentSession
from security.permissions import ORG_TEMPLATES
from security.policies import require_permission
from templates.dependencies import TemplateServiceDep
from templates.enums.template_enums import TemplateChannel
from templates.schemas.template_schemas import (
    TemplateCreateRequest,
    TemplateResponse,
    TemplateUpdateRequest,
)
from users.enums.user_enums import UserRole
from users.schemas.user_session_schema import UserSession

router = APIRouter(prefix="/templates", tags=["Plantillas"])


def _require_admin(session: UserSession, org_id: str) -> None:
    if session.is_global:
        return
    org_entry = session.orgs.get(org_id)
    if org_entry is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin acceso a esta organización")
    if org_entry.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo administradores pueden realizar esta acción")


@router.get("/", response_model=list[TemplateResponse], summary="Listar plantillas de la organización")
async def list_templates(
    session: CurrentSession,
    service: TemplateServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
    channel: Annotated[TemplateChannel | None, Query(alias="channel")] = None,
) -> list[TemplateResponse]:
    require_permission(ORG_TEMPLATES, session, str(organization_id))
    templates = await service.list_by_org(organization_id, channel)
    return [TemplateResponse.model_validate(t) for t in templates]


@router.get("/{template_id}", response_model=TemplateResponse, summary="Obtener plantilla por ID")
async def get_template(
    template_id: uuid.UUID,
    session: CurrentSession,
    service: TemplateServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> TemplateResponse:
    require_permission(ORG_TEMPLATES, session, str(organization_id))
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
    _require_admin(session, str(organization_id))
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
    _require_admin(session, str(organization_id))
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
    _require_admin(session, str(organization_id))
    await service.delete(template_id, organization_id)
