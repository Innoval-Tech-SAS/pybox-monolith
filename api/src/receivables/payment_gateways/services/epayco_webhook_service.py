"""Procesa la confirmación (`urlConfirmation`) de ePayco de `receivables`: verifica la
firma y sincroniza el intento de pago."""

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


class EpaycoWebhookService:
    """Mirror de `PayUWebhookService` -- la confirmación de ePayco también llega como
    campos de formulario planos, verificables sobre el `dict` ya parseado. A
    diferencia de PayU (que acepta nuestra propia `referenceCode` al crear la
    transacción), ePayco solo conoce su propio `ref_payco` -- se busca el intento por
    `provider_transaction_id`, no por `provider_reference`."""

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
            organization_id, ReceivablesGatewayProvider.EPAYCO
        )
        if gateway is None:
            logger.warning(
                "[receivables][epayco-webhook] organizacion sin credenciales ePayco | "
                "org=%s",
                organization_id,
            )
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")

        if not gateway.verify_webhook_signature(fields):
            logger.warning(
                "[receivables][epayco-webhook] firma invalida | org=%s",
                organization_id,
            )
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature")

        ref_payco = str(fields.get("x_ref_payco", ""))
        if not ref_payco:
            logger.warning(
                "[receivables][epayco-webhook] sin x_ref_payco en el payload | "
                "org=%s",
                organization_id,
            )
            return

        # Nunca se confia en el estado del formulario de confirmacion: siempre se
        # reconsulta el estado real contra la API de ePayco (mismo criterio que
        # `WompiWebhookService`/`PayUWebhookService`), aqui por ref_payco.
        transaction = await gateway.get_transaction(ref_payco)

        attempt = await self._attempt_repo.get_by_provider_transaction_id(
            ref_payco, for_update=True
        )
        if attempt is None:
            logger.warning(
                "[receivables][epayco-webhook] sin intento para ref_payco=%s | "
                "org=%s",
                ref_payco,
                organization_id,
            )
            return

        await sync_attempt_with_transaction(
            attempt, transaction, self._attempt_repo, self._payment_repo
        )
