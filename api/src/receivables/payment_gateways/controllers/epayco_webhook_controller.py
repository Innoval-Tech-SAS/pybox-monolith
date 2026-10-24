"""Webhook de ePayco: recibe la confirmación (`urlConfirmation`) de estado de una
transacción."""

import uuid

from fastapi import Request

from core.config.api_router import APIRouter
from receivables.payment_gateways.dependencies import EpaycoWebhookServiceDep

router = APIRouter(prefix="/webhooks/epayco", tags=["Webhooks"])


@router.post(
    "/{organization_id}", summary="Confirmación de ePayco para notificaciones de pago"
)
async def handle_epayco_confirmation(
    organization_id: uuid.UUID,
    request: Request,
    service: EpaycoWebhookServiceDep,
) -> str:
    """Tenant resuelto por la URL (`organization_id`), no por el payload -- mismo
    criterio que `handle_payu_confirmation`. Se manda `methodConfirmation: "POST"` al
    crear cada transacción (ver `EpaycoGateway`) para que la confirmación llegue
    siempre como formulario, nunca como GET+querystring. ePayco solo exige un
    HTTP 200 -- el cuerpo de la respuesta no importa, se devuelve texto plano por
    simetría con los demás webhooks."""
    form = await request.form()
    fields = {key: str(value) for key, value in form.items()}
    await service.process_confirmation(organization_id, fields)
    return "OK"
