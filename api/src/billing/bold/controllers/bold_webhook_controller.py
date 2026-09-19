from typing import Annotated

from fastapi import Header, Request

from core.config.api_router import APIRouter
from billing.bold.services.bold_webhook_service import BoldWebhookService
from billing.invoices.dependencies import InvoiceServiceDep

router = APIRouter(prefix="/webhooks/bold", tags=["Webhooks"])


@router.post("", summary="Webhook de Bold para notificaciones de pago")
async def handle_bold_webhook(
    request: Request,
    service: InvoiceServiceDep,
    x_bold_signature: Annotated[str | None, Header(alias="x-bold-signature")] = None,
) -> dict[str, bool]:
    raw_body = await request.body()
    webhook_service = BoldWebhookService(service)
    await webhook_service.process_webhook(raw_body, x_bold_signature)
    return {"received": True}
