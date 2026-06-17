import json
from typing import Annotated, Any

from fastapi import Header, HTTPException, Request, status

from core.config.api_router import APIRouter
from core.config.logger import logger
from billing.bold.bold_webhook_verifier import verify_bold_signature
from billing.invoices.dependencies import InvoiceServiceDep

router = APIRouter(prefix="/webhooks/bold", tags=["Webhooks"])


@router.post("", summary="Webhook de Bold para notificaciones de pago")
async def handle_bold_webhook(
    request: Request,
    service: InvoiceServiceDep,
    x_bold_signature: Annotated[str | None, Header(alias="x-bold-signature")] = None,
) -> dict[str, bool]:
    raw_body = await request.body()
    if not verify_bold_signature(raw_body, x_bold_signature):
        logger.warning("[billing] firma de webhook Bold invalida")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature")

    try:
        body: dict[str, Any] = json.loads(raw_body) if raw_body else {}
    except json.JSONDecodeError:
        body = {}

    # Bold envia SALE_APPROVED, SALE_REJECTED, VOID_APPROVED, VOID_REJECTED.
    # Solo nos interesa SALE_APPROVED para marcar una factura como pagada.
    event_type = body.get("type", "")
    if event_type != "SALE_APPROVED":
        logger.info("[billing] webhook Bold ignorado | type=%s", event_type)
        return {"received": True}

    # Nuestro orderId se guarda como `reference`; Bold lo retorna en data.metadata.reference
    data = body.get("data") or {}
    metadata = data.get("metadata") or {}
    bold_reference = metadata.get("reference") or ""
    if not bold_reference:
        logger.warning("[billing] webhook Bold SALE_APPROVED sin data.metadata.reference")
        return {"received": True}

    await service.handle_webhook_paid(bold_reference, body)
    return {"received": True}
