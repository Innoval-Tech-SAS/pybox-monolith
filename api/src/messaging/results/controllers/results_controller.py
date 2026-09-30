"""Webhook de notificación de eventos de 360NRS (SMS/Email).

Ver skill `nrs360-provider` para el contrato completo del payload.
"""

from typing import Annotated

from fastapi import Form, HTTPException, Query, status

from core.config.api_router import APIRouter
from messaging.results.dependencies import WebhookServiceDep
from messaging.results.utils.nrs360_webhook_verifier import verify_nrs360_webhook_token

router = APIRouter(prefix="/results", tags=["Resultados de envío"])


@router.post(
    "/webhook",
    summary="Webhook de eventos de entrega de 360NRS",
    include_in_schema=False,
)
async def receive_event(
    service: WebhookServiceDep,
    token: Annotated[str | None, Query()] = None,
    id: Annotated[str, Form()] = "",
    event: Annotated[str, Form()] = "",
    _channel: Annotated[str, Form(alias="channel")] = "",
    _contact_id: Annotated[str, Form(alias="contactId")] = "",
    _campaign_id: Annotated[str, Form(alias="campaignId")] = "",
    _campaign_name: Annotated[str, Form(alias="campaignName")] = "",
    _form_id: Annotated[str, Form(alias="formId")] = "",
    _extra: Annotated[str, Form(alias="extra")] = "",
    _smtp_response: Annotated[str, Form(alias="smtpResponse")] = "",
    _event_date: Annotated[str, Form(alias="eventDate")] = "",
) -> dict:
    """Recibe el evento y actualiza `ContactModel.status`.

    Solo `id`/`event` se usan hoy (ver `WebhookService.handle_event`); el
    resto de los campos que manda 360NRS se aceptan para no romper el POST
    pero no se consumen todavía.
    """
    if not verify_nrs360_webhook_token(token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    await service.handle_event(message_id=id, event=event)
    return {"success": True}
