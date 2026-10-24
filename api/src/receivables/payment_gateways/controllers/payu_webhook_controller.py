"""Webhook de PayU: recibe la confirmación (`notifyUrl`) de estado de una orden."""

import uuid

from fastapi import Request

from core.config.api_router import APIRouter
from receivables.payment_gateways.dependencies import PayUWebhookServiceDep

router = APIRouter(prefix="/webhooks/payu", tags=["Webhooks"])


@router.post(
    "/{organization_id}", summary="Confirmación de PayU para notificaciones de pago"
)
async def handle_payu_confirmation(
    organization_id: uuid.UUID,
    request: Request,
    service: PayUWebhookServiceDep,
) -> str:
    """Tenant resuelto por la URL (`organization_id`), no por el payload -- mismo
    criterio que `handle_bold_webhook`/`handle_wompi_webhook`. PayU postea la
    confirmación como formulario (`application/x-www-form-urlencoded`), no JSON, y
    exige una respuesta de texto plano `"OK"` (no HTML/JSON) -- a diferencia de los
    otros dos webhooks."""
    form = await request.form()
    fields = {key: str(value) for key, value in form.items()}
    await service.process_confirmation(organization_id, fields)
    return "OK"
