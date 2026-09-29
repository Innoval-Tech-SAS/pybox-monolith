"""Procesa el webhook de Bold: verifica la firma y actualiza el intento de pago."""

import json
from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status

from billing.bold.utils.bold_webhook_verifier import verify_bold_signature
from billing.invoices.services.invoice_service import InvoiceService
from core.config.logger import logger


class BoldWebhookService:
    def __init__(self, invoice_service: InvoiceService) -> None:
        self._invoice_service = invoice_service

    async def process_webhook(self, raw_body: bytes, signature: str | None) -> None:
        if not verify_bold_signature(raw_body, signature):
            logger.warning("[billing] firma de webhook Bold invalida")
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature")

        try:
            body: dict[str, Any] = json.loads(raw_body) if raw_body else {}
        except json.JSONDecodeError:
            body = {}

        # Bold envia SALE_APPROVED, SALE_REJECTED, VOID_APPROVED, VOID_REJECTED.
        # Solo nos interesa SALE_APPROVED para marcar una factura como pagada.
        event_type = body.get("type", "")
        if event_type != "SALE_APPROVED":
            logger.info("[billing] webhook Bold ignorado | type=%s", event_type)
            return

        # Nuestro orderId se guarda como `reference`; Bold lo retorna en
        # data.metadata.reference
        data = body.get("data") or {}
        metadata = data.get("metadata") or {}
        bold_reference = metadata.get("reference") or ""
        if not bold_reference:
            logger.warning(
                "[billing] webhook Bold SALE_APPROVED sin data.metadata.reference"
            )
            return

        reported_amount = data.get("amount")
        reported_amount_decimal = (
            Decimal(str(reported_amount)) if reported_amount is not None else None
        )

        await self._invoice_service.mark_attempt_paid(
            "BOLD", bold_reference, reported_amount_decimal, body
        )
