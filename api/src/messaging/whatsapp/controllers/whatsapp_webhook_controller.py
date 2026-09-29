from typing import Annotated, Any

from fastapi import Header, Query, Request
from fastapi.responses import PlainTextResponse

from core.config.api_router import APIRouter
from core.config.logger import logger
from messaging.whatsapp.dependencies import WhatsAppWebhookServiceDep
from messaging.whatsapp.utils.whatsapp_signature import verify_whatsapp_signature

router = APIRouter(prefix="/webhooks/whatsapp", tags=["Webhooks"])


@router.get("", include_in_schema=False)
async def verify_whatsapp_webhook(
    service: WhatsAppWebhookServiceDep,
    hub_mode: Annotated[str | None, Query(alias="hub.mode")] = None,
    hub_verify_token: Annotated[str | None, Query(alias="hub.verify_token")] = None,
    hub_challenge: Annotated[str | None, Query(alias="hub.challenge")] = None,
) -> PlainTextResponse:
    challenge = service.verify(hub_mode, hub_verify_token, hub_challenge)
    return PlainTextResponse(challenge)


@router.post("", include_in_schema=False)
async def receive_whatsapp_webhook(
    request: Request,
    service: WhatsAppWebhookServiceDep,
    x_hub_signature_256: Annotated[
        str | None, Header(alias="X-Hub-Signature-256")
    ] = None,
) -> dict[str, bool]:
    raw_body = await request.body()
    if not verify_whatsapp_signature(raw_body, x_hub_signature_256):
        logger.warning("[whatsapp_webhook] firma inválida, evento ignorado")
        return {"received": True}

    body: dict[str, Any] = (await request.json()) if raw_body else {}
    await service.handle_event(body)
    return {"received": True}
