"""Procesa la confirmación (`notifyUrl`) de PayU de `receivables`: verifica la firma y
sincroniza el intento de pago."""

import uuid
from typing import Any

from fastapi import HTTPException, status

from core.config.logger import logger
from receivables.payment_gateways.enums.payment_gateway_enums import (
    ReceivablesGatewayProvider,
)
from receivables.payment_gateways.gateways.resolver import ReceivablesGatewayResolver
from receivables.payment_gateways.repository.payment_attempt_repository import (
    CreditPaymentAttemptRepository,
)
from receivables.payment_gateways.utils.attempt_status_sync import (
    sync_attempt_with_transaction,
)
from receivables.payments.repository.payment_repository import PaymentRepository


class PayUWebhookService:
    """Mirror de `WompiWebhookService` para PayU -- a diferencia de
    `BoldWebhookService`, la firma de PayU SÍ se puede verificar sobre el `dict` ya
    parseado (`ReceivablesPaymentGateway.verify_webhook_signature`), porque su
    confirmación llega como campos de formulario planos, no como bytes crudos más
    header."""

    def __init__(
        self,
        gateway_resolver: ReceivablesGatewayResolver,
        attempt_repo: CreditPaymentAttemptRepository,
        payment_repo: PaymentRepository,
    ) -> None:
        self._gateway_resolver = gateway_resolver
        self._attempt_repo = attempt_repo
        self._payment_repo = payment_repo

    async def process_confirmation(
        self, organization_id: uuid.UUID, fields: dict[str, Any]
    ) -> None:
        gateway = await self._gateway_resolver.get_for_organization(
            organization_id, ReceivablesGatewayProvider.PAYU
        )
        if gateway is None:
            logger.warning(
                "[receivables][payu-webhook] organizacion sin credenciales PayU | "
                "org=%s",
                organization_id,
            )
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")

        if not gateway.verify_webhook_signature(fields):
            logger.warning(
                "[receivables][payu-webhook] firma invalida | org=%s", organization_id
            )
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature")

        reference = str(fields.get("reference_sale", ""))
        if not reference:
            logger.warning(
                "[receivables][payu-webhook] sin reference_sale en el payload | "
                "org=%s",
                organization_id,
            )
            return

        # Nunca se confia en el estado del formulario de confirmacion: siempre se
        # reconsulta el estado real contra la API de PayU (mismo criterio que
        # `WompiWebhookService`/`BoldWebhookService`), aqui por referenceCode.
        transaction = await gateway.get_transaction(reference)

        attempt = await self._attempt_repo.get_by_provider_reference(
            reference, for_update=True
        )
        if attempt is None:
            logger.warning(
                "[receivables][payu-webhook] sin intento para reference=%s | org=%s",
                reference,
                organization_id,
            )
            return

        await sync_attempt_with_transaction(
            attempt, transaction, self._attempt_repo, self._payment_repo
        )
