import uuid

from fastapi import Request

from core.config.api_router import APIRouter
from receivables.payment_gateways.dependencies import WompiWebhookServiceDep

router = APIRouter(prefix="/webhooks/wompi", tags=["Webhooks"])


@router.post("/{organization_id}", summary="Webhook de Wompi para notificaciones de transacción")
async def handle_wompi_webhook(
    organization_id: uuid.UUID,
    request: Request,
    service: WompiWebhookServiceDep,
) -> dict[str, bool]:
    """Tenant resuelto por la URL (`organization_id`), no por el payload — ver skill
    `wompi-gateway`, Paso 7, y `WompiWebhookService` para el porqué. Cada organización
    registra su propia URL única en su cuenta Wompi."""
    body = await request.json()
    await service.process_webhook(organization_id, body)
    return {"received": True}
