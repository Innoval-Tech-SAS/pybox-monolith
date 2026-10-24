"""Procesa el webhook de Bold de `receivables`: verifica la firma y sincroniza el
intento de pago."""

import json
import uuid

from fastapi import HTTPException, status

from core.config.logger import logger
from receivables.payment_gateways.enums.payment_gateway_enums import (
    ReceivablesGatewayProvider,
)
from receivables.payment_gateways.gateways.bold.bold_signature import (
    verify_bold_webhook_signature,
)
from receivables.payment_gateways.gateways.resolver import ReceivablesGatewayResolver
from receivables.payment_gateways.repository.payment_attempt_repository import (
    CreditPaymentAttemptRepository,
)
from receivables.payment_gateways.services.payment_gateway_credential_service import (
    OrganizationGatewayCredentialService,
)
from receivables.payment_gateways.utils.attempt_status_sync import (
    sync_attempt_with_transaction,
)
from receivables.payments.repository.payment_repository import PaymentRepository


class BoldWebhookService:
    """Mirror de `WompiWebhookService` para Bold. La firma de Bold se calcula sobre
    los bytes crudos del body y un header (`x-bold-signature`) -- a diferencia del
    checksum de Wompi, no se puede verificar a través de
    `ReceivablesPaymentGateway.verify_webhook_signature` (que solo recibe el `dict` ya
    parseado), así que este servicio resuelve la credencial decifrada directamente
    para el secreto, y usa `ReceivablesGatewayResolver` solo para la reconsulta
    posterior del estado real contra la API de Bold."""

    def __init__(
        self,
        credential_service: OrganizationGatewayCredentialService,
        gateway_resolver: ReceivablesGatewayResolver,
        attempt_repo: CreditPaymentAttemptRepository,
        payment_repo: PaymentRepository,
    ) -> None:
        self._credential_service = credential_service
        self._gateway_resolver = gateway_resolver
        self._attempt_repo = attempt_repo
        self._payment_repo = payment_repo

    async def process_webhook(
        self,
        organization_id: uuid.UUID,
        raw_body: bytes,
        signature_header: str | None,
    ) -> None:
        credentials = await self._credential_service.get_decrypted(
            organization_id, ReceivablesGatewayProvider.BOLD
        )
        if credentials is None:
            # 404 generico: mismo criterio que el webhook de Wompi (ver
            # `WompiWebhookService`) -- no confirma ni que la organizacion exista ni
            # que tenga Bold configurado.
            logger.warning(
                "[receivables][bold-webhook] organizacion sin credenciales Bold | "
                "org=%s",
                organization_id,
            )
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")

        secret_key = credentials.get("secret_key") or ""
        if not verify_bold_webhook_signature(raw_body, signature_header, secret_key):
            logger.warning(
                "[receivables][bold-webhook] firma invalida | org=%s", organization_id
            )
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature")

        try:
            body = json.loads(raw_body) if raw_body else {}
        except json.JSONDecodeError:
            body = {}

        reference = str(
            ((body.get("data") or {}).get("metadata") or {}).get("reference", "")
        )
        if not reference:
            logger.warning(
                "[receivables][bold-webhook] sin metadata.reference en el payload | "
                "org=%s",
                organization_id,
            )
            return

        # Nunca se confia en el estado del body del webhook: siempre se reconsulta el
        # estado real contra la API de Bold (mismo criterio que
        # `WompiWebhookService`), aqui por `reference_id` -- ver nota en
        # `BoldGateway.get_transaction`.
        gateway = await self._gateway_resolver.get_for_organization(
            organization_id, ReceivablesGatewayProvider.BOLD
        )
        if gateway is None:
            return
        transaction = await gateway.get_transaction(reference)

        attempt = await self._attempt_repo.get_by_provider_transaction_id(
            transaction.id, for_update=True
        )
        if attempt is None:
            logger.warning(
                "[receivables][bold-webhook] sin intento para reference=%s | org=%s",
                reference,
                organization_id,
            )
            return

        await sync_attempt_with_transaction(
            attempt, transaction, self._attempt_repo, self._payment_repo
        )
