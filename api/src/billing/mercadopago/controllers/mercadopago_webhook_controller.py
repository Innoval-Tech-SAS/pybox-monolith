from typing import Annotated, Any

from fastapi import Depends, Header, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.config.api_router import APIRouter
from core.config.logger import logger
from core.database.database import get_main_session
from billing.invoices.dependencies import InvoiceServiceDep
from billing.mercadopago.services.mercadopago_webhook_service import MercadoPagoWebhookService

router = APIRouter(prefix="/webhooks/mercadopago", tags=["Webhooks"])


@router.post("", summary="Webhook de Mercado Pago para notificaciones de orders")
async def handle_mercadopago_webhook(
    request: Request,
    service: InvoiceServiceDep,
    session: Annotated[AsyncSession, Depends(get_main_session)],
    data_id: Annotated[str | None, Query(alias="data.id")] = None,
    x_signature: Annotated[str | None, Header(alias="x-signature")] = None,
    x_request_id: Annotated[str | None, Header(alias="x-request-id")] = None,
) -> dict[str, bool]:
    logger.info(
        "[billing][mp-webhook] recibido | data_id=%s x_request_id=%s query=%s",
        data_id, x_request_id, dict(request.query_params),
    )

    raw_body = await request.body()
    try:
        body: dict[str, Any] = (await request.json()) if raw_body else {}
    except ValueError:
        body = {}

    webhook_service = MercadoPagoWebhookService(service, session)
    await webhook_service.process_webhook(body, data_id, x_signature, x_request_id)

    return {"received": True}
