from typing import Annotated

from fastapi import Form

from core.config.api_router import APIRouter
from messaging.results.dependencies import WebhookServiceDep

router = APIRouter(prefix="/results", tags=["Resultados de envío"])


@router.post(
    "/webhook",
    summary="Webhook de eventos de entrega de 360NRS",
    include_in_schema=False,
)
async def receive_event(
    service: WebhookServiceDep,
    id: Annotated[str, Form()] = "",
    event: Annotated[str, Form()] = "",
    channel: Annotated[str, Form()] = "",
    contactId: Annotated[str, Form()] = "",
    campaignId: Annotated[str, Form()] = "",
    campaignName: Annotated[str, Form()] = "",
    formId: Annotated[str, Form()] = "",
    extra: Annotated[str, Form()] = "",
    smtpResponse: Annotated[str, Form()] = "",
    eventDate: Annotated[str, Form()] = "",
) -> dict:
    await service.handle_event(message_id=id, event=event)
    return {"success": True}
