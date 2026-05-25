import asyncio

from fastapi import APIRouter, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from notifications.dependencies import NotificationServiceDep
from notifications.schemas.notification_schemas import NotificationSchema
from security.dependencies import CurrentSession, SSESession
from sse.sse_emitter import sse_emitter

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationSchema])
async def list_notifications(session: CurrentSession, service: NotificationServiceDep):
    return await service.get_notifications(session.user_id)


@router.post("/read-all", status_code=204)
async def mark_all_read(session: CurrentSession, service: NotificationServiceDep):
    await service.mark_all_read(session.user_id)


@router.get("/stream")
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


@router.get("/{notification_id}", response_model=NotificationSchema)
async def get_notification(
    notification_id: int,
    session: CurrentSession,
    service: NotificationServiceDep,
):
    n = await service.get_notification(notification_id, session.user_id)
    if not n:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")
    return n
