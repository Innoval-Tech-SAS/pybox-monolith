"""Webhook de Helena: recibe eventos de llamadas y campañas IVR."""

import json
from typing import Annotated, Any

from fastapi import Header, HTTPException, Request, status

from core.config.api_router import APIRouter
from core.config.logger import logger
from messaging.ivr.dependencies import IvrEventServiceDep
from messaging.ivr.utils.helena_webhook_verifier import verify_helena_signature

router = APIRouter(prefix="/webhooks/helena", tags=["Webhooks"])


@router.post(
    "",
    summary="Webhook de eventos de llamadas IVR de Helena",
    include_in_schema=False,
)
async def handle_helena_webhook(
    request: Request,
    service: IvrEventServiceDep,
    x_helena_signature: Annotated[
        str | None, Header(alias="x-helena-signature")
    ] = None,
) -> dict[str, bool]:
    """Recibe los eventos de Helena y los delega al servicio de ingesta.

    Responde `200` siempre que la firma sea válida, aunque el procesamiento
    falle. Helena solo reintenta ante errores de red, no ante `5xx`, y cada
    fallo incrementa un contador que a las 1001 fallas desactiva el webhook:
    devolver un error aquí no recupera el evento y sí degrada la integración.
    Los fallos de procesamiento quedan en el log.
    """
    raw_body = await request.body()

    if not verify_helena_signature(raw_body, x_helena_signature):
        logger.warning("[ivr_webhook] firma inválida, evento rechazado")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature")

    try:
        body: dict[str, Any] = json.loads(raw_body) if raw_body else {}
    except json.JSONDecodeError:
        logger.warning("[ivr_webhook] cuerpo no es JSON válido")
        return {"received": True}

    await service.handle_event(body)
    return {"received": True}
