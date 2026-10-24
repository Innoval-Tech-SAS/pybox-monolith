"""Sincroniza un intento de pago con el estado real de la transacción en la pasarela.

Compartido por `WompiWebhookService`/`BoldWebhookService` (entrega del webhook) y
`PaymentCheckoutService.refresh_attempt_status` (polling del self-service) -- todos
necesitan la misma regla, sin importar la pasarela: nunca confiar en un estado ya
visto, congelar el monto esperado al crear el intento y nunca marcarlo `APPROVED` si el
monto reportado no coincide (skill `wompi-gateway`, Paso 7, para el caso de Wompi)."""

from datetime import datetime, timezone

from core.config.logger import logger
from receivables.payment_gateways.enums.payment_gateway_enums import (
    ReceivablesPaymentAttemptStatus,
)
from receivables.payment_gateways.gateways.base import GatewayTransaction
from receivables.payment_gateways.models.payment_attempt_model import (
    CreditPaymentAttemptModel,
)
from receivables.payment_gateways.repository.payment_attempt_repository import (
    CreditPaymentAttemptRepository,
)
from receivables.payment_gateways.utils.wompi_status_mapping import to_attempt_status
from receivables.payments.enums.payment_enums import PaymentStatus
from receivables.payments.repository.payment_repository import PaymentRepository


async def sync_attempt_with_transaction(
    attempt: CreditPaymentAttemptModel,
    transaction: GatewayTransaction,
    attempt_repo: CreditPaymentAttemptRepository,
    payment_repo: PaymentRepository,
) -> None:
    if attempt.status == ReceivablesPaymentAttemptStatus.APPROVED:
        return  # idempotencia: ya se proceso una sincronizacion anterior.

    new_status = to_attempt_status(transaction.status)
    if new_status == ReceivablesPaymentAttemptStatus.APPROVED:
        if (
            attempt.expected_amount_cents is not None
            and transaction.amount_in_cents != attempt.expected_amount_cents
        ):
            logger.warning(
                "[receivables] monto no coincide | intento=%s esperado=%s "
                "reportado=%s",
                attempt.id,
                attempt.expected_amount_cents,
                transaction.amount_in_cents,
            )
            new_status = ReceivablesPaymentAttemptStatus.ERROR

    attempt.status = new_status
    attempt.provider_payload = transaction.raw
    await attempt_repo.update(attempt)

    if new_status != ReceivablesPaymentAttemptStatus.APPROVED:
        return

    payment = await payment_repo.get_by_id(attempt.payment_id)
    if payment is not None and payment.status != PaymentStatus.PAID:
        payment.status = PaymentStatus.PAID
        payment.payment_date = datetime.now(timezone.utc)
        await payment_repo.update(payment)
