"""Endpoints de notificaciones judiciales: buzón del deudor y panel de la entidad."""

import uuid
from typing import Annotated

from fastapi import File, Response, UploadFile, status

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from receivables.judicial_notifications.dependencies import (
    JudicialNotificationServiceDep,
    RequireSelf,
)
from receivables.judicial_notifications.schemas.judicial_notification_schemas import (
    JudicialInboxResponse,
    JudicialNotificationCreate,
    JudicialNotificationResponse,
    JudicialPriorityOption,
)

router = APIRouter(prefix="/judicial-notifications", tags=["Buzón judicial"])


@router.get(
    "/priorities",
    response_model=list[JudicialPriorityOption],
    summary="Listar prioridades judiciales",
    description=(
        "Catálogo código→etiqueta de prioridades, para el select del panel de "
        "la entidad y el chip del buzón. Declarado antes de las rutas con "
        "{notification_id} para que no se resuelva como un UUID."
    ),
)
async def list_priorities(
    _: CurrentSession,
    service: JudicialNotificationServiceDep,
) -> list[JudicialPriorityOption]:
    return service.list_priorities()


@router.get(
    "/mine",
    response_model=JudicialInboxResponse,
    summary="Buzón judicial del titular",
    description=(
        "Notificaciones judiciales de los créditos del titular autenticado "
        "(como deudor o codeudor), de la más reciente a la más antigua, con el "
        "contador de no leídas."
    ),
)
async def my_inbox(
    session: RequireSelf,
    service: JudicialNotificationServiceDep,
) -> JudicialInboxResponse:
    return await service.get_my_inbox(session)


@router.post(
    "/read-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Marcar todo el buzón como leído",
)
async def mark_all_read(
    session: RequireSelf,
    service: JudicialNotificationServiceDep,
) -> None:
    await service.mark_all_read(session)


@router.post(
    "/{notification_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Marcar una notificación como leída",
)
async def mark_read(
    notification_id: uuid.UUID,
    session: RequireSelf,
    service: JudicialNotificationServiceDep,
) -> None:
    await service.mark_read(session, notification_id)


@router.post(
    "",
    response_model=JudicialNotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Emitir una notificación judicial",
    description="La entidad acreedora emite una notificación sobre un crédito propio. "
    "Requiere el permiso portfolio.judicial sobre la organización dueña del crédito.",
)
async def create_notification(
    body: JudicialNotificationCreate,
    session: CurrentSession,
    service: JudicialNotificationServiceDep,
) -> JudicialNotificationResponse:
    return await service.create(session, body)


@router.get(
    "/credits/{credit_id}",
    response_model=list[JudicialNotificationResponse],
    summary="Notificaciones emitidas sobre un crédito",
    description=(
        "Listado del lado de la entidad. Requiere el permiso portfolio.judicial."
    ),
)
async def list_by_credit(
    credit_id: uuid.UUID,
    session: CurrentSession,
    service: JudicialNotificationServiceDep,
) -> list[JudicialNotificationResponse]:
    return await service.list_by_credit(session, credit_id)


@router.post(
    "/{notification_id}/attachments",
    response_model=JudicialNotificationResponse,
    summary="Adjuntar archivos a una notificación judicial",
    description="Solo la entidad emisora puede adjuntar soporte documental. "
    "Requiere el permiso portfolio.judicial sobre la organización dueña del crédito.",
)
async def upload_attachments(
    notification_id: uuid.UUID,
    files: Annotated[list[UploadFile], File()],
    session: CurrentSession,
    service: JudicialNotificationServiceDep,
) -> JudicialNotificationResponse:
    return await service.upload_attachments(session, notification_id, files)


@router.get(
    "/{notification_id}/documents/{document_id}/content",
    summary="Descargar un adjunto de una notificación judicial",
    description=(
        "El titular descarga los adjuntos de sus propias notificaciones; la "
        "entidad, los de los créditos sobre los que tiene el permiso "
        "portfolio.judicial."
    ),
    response_class=Response,
)
async def get_attachment_content(
    notification_id: uuid.UUID,
    document_id: uuid.UUID,
    session: CurrentSession,
    service: JudicialNotificationServiceDep,
) -> Response:
    return await service.get_attachment_content(session, notification_id, document_id)
