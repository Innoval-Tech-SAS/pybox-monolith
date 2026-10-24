"""Webhook de Bold: recibe notificaciones de estado de un pago."""

import uuid

from fastapi import Header, Request

from core.config.api_router import APIRouter
from receivables.payment_gateways.dependencies import BoldWebhookServiceDep

router = APIRouter(prefix="/webhooks/bold", tags=["Webhooks"])


@router.post(
    "/{organization_id}", summary="Webhook de Bold para notificaciones de pago"
)
async def handle_bold_webhook(
    organization_id: uuid.UUID,
    request: Request,
    service: BoldWebhookServiceDep,
    x_bold_signature: str | None = Header(default=None, alias="x-bold-signature"),
) -> dict[str, bool]:
    """Tenant resuelto por la URL (`organization_id`), no por el payload -- mismo
    criterio que `handle_wompi_webhook`. La firma de Bold exige los bytes crudos del
    body (ver `verify_bold_webhook_signature`), por eso se lee con `request.body()` y
    no con `request.json()`."""
    raw_body = await request.body()
    await service.process_webhook(organization_id, raw_body, x_bold_signature)
    return {"received": True}
