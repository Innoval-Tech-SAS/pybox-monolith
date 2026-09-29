"""Procesa el webhook de Mercado Pago: verifica firma y actualiza el intento de pago."""

from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from billing.invoices.services.invoice_service import InvoiceService
from billing.mercadopago.services.mercadopago_client import MercadoPagoClient
from billing.mercadopago.utils.mercadopago_credentials import (
    resolve_credentials_for_application_id,
)
from billing.mercadopago.utils.mercadopago_status_mapper import (
    mercadopago_order_status_to_attempt_status,
)
from billing.mercadopago.utils.mercadopago_webhook_verifier import (
    verify_mercadopago_signature,
)
from core.config.logger import logger
from core.tools.config_tools import get_or_throw


class MercadoPagoWebhookService:
    def __init__(self, invoice_service: InvoiceService, session: AsyncSession) -> None:
        self._invoice_service = invoice_service
        self._session = session
        self._client = MercadoPagoClient()

    async def process_webhook(
        self,
        body: dict[str, Any],
        data_id: str | None,
        x_signature: str | None,
        x_request_id: str | None,
    ) -> None:
        # El body todavia no esta autenticado en este punto, pero solo se usa para leer
        # `application_id` (identifica que cuenta/pais de MP origino la notificacion) y
        # resolver con que webhook_secret verificar la firma a continuacion. Un atacante
        # no gana nada falseando este campo: igual necesita el secret real para pasar
        # `verify_mercadopago_signature`.
        application_id = str(body.get("application_id", ""))
        logger.info(
            "[billing][mp-webhook] paso=resolver_credenciales inicio | "
            "application_id=%s",
            application_id,
        )
        credentials = await resolve_credentials_for_application_id(
            self._session, application_id
        )
        logger.info(
            "[billing][mp-webhook] paso=resolver_credenciales fin | "
            "application_id=%s pais=%s",
            application_id,
            credentials.country if credentials else None,
        )
        if credentials is None:
            logger.warning(
                "[billing][mp-webhook] application_id desconocido | application_id=%s",
                application_id,
            )
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature")

        # En sandbox las notificaciones de la Orders API las firma MP con un secret
        # que NO es el "Modo de prueba" visible en el panel (a veces el del test
        # user, a veces el productivo: llegan incluso con live_mode=True), asi que
        # la firma nunca cuadra con nuestro `webhook_secret`. Por eso el gate es el
        # ENTORNO, no `live_mode`: en produccion se exige firma valida; fuera de
        # produccion se deja pasar. No es un hueco de seguridad: mas abajo
        # `get_order` reconsulta el estado real a la API de MP con el
        # access_token secreto, asi que un webhook falso no puede inventar un pago
        # (id inexistente -> 404, id real -> estado real).
        is_production = get_or_throw("ENV") == "production"
        logger.info(
            "[billing][mp-webhook] paso=verificar_firma inicio | "
            "data_id=%s produccion=%s",
            data_id,
            is_production,
        )
        firma_valida = bool(data_id) and verify_mercadopago_signature(
            data_id, x_request_id, x_signature, credentials.webhook_secret
        )
        logger.info(
            "[billing][mp-webhook] paso=verificar_firma fin | resultado=%s",
            firma_valida,
        )
        if not firma_valida:
            if is_production:
                logger.warning(
                    "[billing][mp-webhook] firma invalida | data_id=%s", data_id
                )
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature")
            logger.warning(
                "[billing][mp-webhook] firma invalida en entorno no-productivo: "
                "se continua; el estado se confirma via get_order | data_id=%s",
                data_id,
            )

        # Solo nos interesa el topico "order" (Orders API); otros topicos de la misma
        # aplicacion (payment, merchant_order, etc.) se ignoran aqui.
        event_type = body.get("type", "")
        if event_type != "order":
            logger.info("[billing][mp-webhook] ignorado | type=%s", event_type)
            return

        # El webhook solo trae el id de la order, sin status ni monto: hay que
        # consultar el detalle para confirmar el estado real antes de aplicar
        # cualquier transicion.
        logger.info("[billing][mp-webhook] paso=get_order inicio | data_id=%s", data_id)
        order = await self._client.get_order(credentials.access_token, data_id)
        # No se loguea `order` completo: trae el email del pagador y el detalle de la
        # transacción en texto plano, y este log queda en texto plano de forma
        # permanente.
        logger.info(
            "[billing][mp-webhook] paso=get_order fin | order_id=%s status=%s",
            order.get("id"),
            order.get("status"),
        )

        order_status = order.get("status", "")
        attempt_status = mercadopago_order_status_to_attempt_status(order_status)
        logger.info(
            "[billing][mp-webhook] paso=mapear_estado fin | "
            "order_status=%s attempt_status=%s",
            order_status,
            attempt_status,
        )
        if attempt_status is None:
            logger.info(
                "[billing][mp-webhook] sin mapeo de estado | id=%s status=%s",
                data_id,
                order_status,
            )
            return

        payments = (order.get("transactions") or {}).get("payments") or []
        reported_amount = Decimal(str(payments[0]["amount"])) if payments else None

        logger.info(
            "[billing][mp-webhook] paso=sync_attempt inicio | data_id=%s "
            "attempt_status=%s reported_amount=%s",
            data_id,
            attempt_status,
            reported_amount,
        )
        await self._invoice_service.sync_attempt_status_by_link_id(
            "MERCADO_PAGO", data_id, attempt_status, reported_amount, order
        )
        logger.info("[billing][mp-webhook] paso=sync_attempt fin | data_id=%s", data_id)
