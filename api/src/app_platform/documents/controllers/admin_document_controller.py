"""Endpoints admin de la papelera global de documentos (todos los dominios)."""

import uuid

from fastapi import status

from app_platform.documents.dependencies import AdminDocumentServiceDep
from app_platform.documents.schemas.admin_document_schemas import (
    TrashedDocumentDomain,
    TrashedDocumentListResponse,
)
from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_global_admin

router = APIRouter(prefix="/admin/documents", tags=["Documentos (Admin Global)"])


@router.get(
    "/trash",
    response_model=TrashedDocumentListResponse,
    summary="Papelera de documentos",
    description=(
        "Documentos dados de baja en cualquiera de los dominios (deudor, "
        "ticket, portafolio, notificación judicial, ejecución de reporte) "
        "más los de la entidad sin tabla de unión. Solo administradores "
        "globales."
    ),
)
async def list_trash(
    session: CurrentSession,
    service: AdminDocumentServiceDep,
) -> TrashedDocumentListResponse:
    require_global_admin(session)
    return await service.list_trash()


@router.post(
    "/{domain}/{entity_id}/restore",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Restaurar un documento de la papelera",
    description=(
        "Deshace la baja lógica del enlace de dominio y de su fila de "
        "metadatos. Los bytes nunca se borraron al dar de baja, así que la "
        "restauración es completa. Solo administradores globales."
    ),
)
async def restore_document(
    domain: TrashedDocumentDomain,
    entity_id: uuid.UUID,
    session: CurrentSession,
    service: AdminDocumentServiceDep,
) -> None:
    require_global_admin(session)
    await service.restore(domain, entity_id)
