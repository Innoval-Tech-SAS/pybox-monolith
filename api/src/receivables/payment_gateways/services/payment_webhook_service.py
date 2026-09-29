import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status

from core.config.logger import logger
from receivables.payment_gateways.enums.payment_gateway_enums import (
    ReceivablesGatewayProvider,
    ReceivablesPaymentAttemptStatus,
)
from receivables.payment_gateways.gateways.resolver import ReceivablesGatewayResolver
from receivables.payment_gateways.repository.payment_attempt_repository import CreditPaymentAttemptRepository
from receivables.payment_gateways.utils.wompi_status_mapping import to_attempt_status
from receivables.payments.enums.payment_enums import PaymentStatus
from receivables.payments.repository.payment_repository import PaymentRepository


class WompiWebhookService:
    """Mirror de `MercadoPagoWebhookService` (billing) para el webhook de Wompi de
    `receivables`. Resuelve el tenant por la URL (`organization_id`), NO por el
    payload — la doc de Wompi tiene una discrepancia sin confirmar sobre si
    `data.transaction` trae `merchant_id` (skill `wompi-gateway`, Paso 7); este diseño
    no depende de eso para nada, ni siquiera para autorizar (mismo razonamiento que
    Mercado Pago: un `organization_id` ajeno en la URL no gana nada — la firma solo
    cuadra con el `events_secret` real de esa organización)."""

    def __init__(
        self,
        gateway_resolver: ReceivablesGatewayResolver,
        attempt_repo: CreditPaymentAttemptRepository,
        payment_repo: PaymentRepository,
    ) -> None:
        self._gateway_resolver = gateway_resolver
        self._attempt_repo = attempt_repo
        self._payment_repo = payment_repo

    async def process_webhook(self, organization_id: uuid.UUID, body: dict[str, Any]) -> None:
        gateway = await self._gateway_resolver.get_for_organization(organization_id, ReceivablesGatewayProvider.WOMPI)
        if gateway is None:
            # 404 generico: ni confirma que la organizacion existe ni que tiene Wompi
            # configurado (mismo criterio que un recurso de otro tenant, ver skill
            # `tenant-isolation`).
            logger.warning(
                "[receivables][wompi-webhook] organizacion sin credenciales Wompi | org=%s", organization_id
            )
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")

        if not gateway.verify_webhook_signature(body):
            logger.warning("[receivables][wompi-webhook] firma invalida | org=%s", organization_id)
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature")

        transaction_id = str(((body.get("data") or {}).get("transaction") or {}).get("id", ""))
        if not transaction_id:
            logger.warning("[receivables][wompi-webhook] sin transaction id en el payload | org=%s", organization_id)
            return

        # Nunca se confia en el estado/monto del body: siempre se reconsulta el estado
        # real contra la API de Wompi con la llave privada de la organizacion (skill
        # `wompi-gateway`, Paso 7).
        transaction = await gateway.get_transaction(transaction_id)

        # for_update=True: dos entregas concurrentes del mismo webhook (reintento tipico
        # de las pasarelas) no deben poder pasar ambas la validacion de monto — la
        # segunda espera el lock y lee el estado ya actualizado por la primera.
        attempt = await self._attempt_repo.get_by_provider_transaction_id(transaction.id, for_update=True)
        if attempt is None:
            logger.warning(
                "[receivables][wompi-webhook] sin intento para transaction_id=%s | org=%s",
                transaction.id, organization_id,
            )
            return

        if attempt.status == ReceivablesPaymentAttemptStatus.APPROVED:
            return  # idempotencia: ya se proceso una entrega anterior de este webhook.

        new_status = to_attempt_status(transaction.status)
        if new_status == ReceivablesPaymentAttemptStatus.APPROVED:
            if attempt.expected_amount_cents is not None and transaction.amount_in_cents != attempt.expected_amount_cents:
                logger.warning(
                    "[receivables][wompi-webhook] monto no coincide | intento=%s esperado=%s reportado=%s",
                    attempt.id, attempt.expected_amount_cents, transaction.amount_in_cents,
                )
                new_status = ReceivablesPaymentAttemptStatus.ERROR

        attempt.status = new_status
        attempt.provider_payload = transaction.raw
        await self._attempt_repo.update(attempt)

        if new_status != ReceivablesPaymentAttemptStatus.APPROVED:
            return

        payment = await self._payment_repo.get_by_id(attempt.payment_id)
        if payment is not None and payment.status != PaymentStatus.PAID:
            payment.status = PaymentStatus.PAID
            payment.payment_date = datetime.now(timezone.utc)
            await self._payment_repo.update(payment)
