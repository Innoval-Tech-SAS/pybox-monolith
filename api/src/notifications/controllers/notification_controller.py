import asyncio

from fastapi import APIRouter, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from notifications.dependencies import NotificationServiceDep
from notifications.schemas.notification_schemas import NotificationSchema
from security.dependencies import CurrentSession, SSESession
from sse.sse_emitter import sse_emitter

router = APIRouter(prefix="/notifications", tags=["Notificaciones"])


@router.get(
    "",
    response_model=list[NotificationSchema],
    summary="Listar notificaciones del usuario",
)
async def list_notifications(session: CurrentSession, service: NotificationServiceDep):
    return await service.get_notifications(session.user_id)


@router.post("/read-all", status_code=204, summary="Marcar todas las notificaciones como leídas")
async def mark_all_read(session: CurrentSession, service: NotificationServiceDep):
    await service.mark_all_read(session.user_id)


@router.get(
    "/stream",
    summary="Stream de notificaciones en tiempo real (SSE)",
    description="Conexión Server-Sent Events para recibir notificaciones en tiempo real.",
)
async def notification_stream(session: SSESession):
    user_id = session.user_id
    queue = sse_emitter.subscribe(user_id)

    async def generator():
        try:
            while True:
                data = await queue.get()
                yield data
        except asyncio.CancelledError:
            pass
        finally:
            sse_emitter.unsubscribe(user_id, queue)

    return EventSourceResponse(generator())


@router.get(
    "/{notification_id}",
    response_model=NotificationSchema,
    summary="Obtener notificación por ID",
)
async def get_notification(
    notification_id: int,
    session: CurrentSession,
    service: NotificationServiceDep,
):
    n = await service.get_notification(notification_id, session.user_id)
    if not n:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")
    return n
