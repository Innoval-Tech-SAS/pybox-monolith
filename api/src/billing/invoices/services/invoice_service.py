import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config.logger import logger
from core.tools.config_tools import get_or_throw
from billing.bold.bold_client import generate_integrity_hash
from billing.bold.bold_status_mapper import attempt_status_to_invoice_transition, is_attempt_reusable
from billing.invoices.enums.invoice_enums import InvoiceStatus, PaymentAttemptStatus
from billing.invoices.models.invoice_model import InvoiceModel
from billing.invoices.models.invoice_item_model import InvoiceItemModel
from billing.invoices.models.payment_attempt_model import PaymentAttemptModel
from billing.invoices.repository.invoice_repository import InvoiceRepository
from billing.invoices.repository.payment_attempt_repository import PaymentAttemptRepository
from billing.invoices.schemas.invoice_schemas import ListInvoicesResponse, PaymentLinkResponse
from messaging.contacts.repositories.contact_repository import ContactRepository

# Reutilizar un intento solo si el enlace sigue activo y tiene menos de 1 hora de antiguedad.
# Bold elimina referencias de prueba a las 12 h; se usa 1 h para ser conservadores.
_ATTEMPT_TTL = timedelta(hours=1)


@dataclass
class InvoiceItemInput:
    campaign_id: uuid.UUID | None
    campaign_name: str
    channel_id: uuid.UUID
    channel_name: str
    base_currency: str
    quantity: int
    subtotal_base: Decimal


@dataclass
class CreateInvoiceParams:
    organization_id: uuid.UUID
    period_year: int
    period_month: int
    exchange_rate: Decimal
    items: list[InvoiceItemInput] = field(default_factory=list)


def _round_pesos(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _to_base36(value: int) -> str:
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    if value == 0:
        return "0"
    chars = []
    while value:
        value, rem = divmod(value, 36)
        chars.append(digits[rem])
    return "".join(reversed(chars)).upper()


class InvoiceService:
    def __init__(
        self,
        session: AsyncSession,
        invoice_repo: InvoiceRepository,
        attempt_repo: PaymentAttemptRepository,
        contact_repo: ContactRepository,
    ):
        self._session = session
        self._invoice_repo = invoice_repo
        self._attempt_repo = attempt_repo
        self._contact_repo = contact_repo

    # -- Consulta --------------------------------------------------------------

    async def get_current_invoice(self, organization_id: uuid.UUID) -> InvoiceModel | None:
        return await self._invoice_repo.get_current_by_organization_id(organization_id)

    async def list_invoices(self, organization_id: uuid.UUID, page: int, limit: int) -> ListInvoicesResponse:
        invoices, total = await self._invoice_repo.list_by_organization_id(organization_id, page, limit)
        return ListInvoicesResponse(
            invoices=invoices,  # type: ignore[arg-type]
            total=total,
            page=page,
            limit=limit,
            total_pages=-(-total // limit) if limit else 0,
        )

    async def get_invoice(self, id: uuid.UUID, organization_id: uuid.UUID) -> InvoiceModel:
        invoice = await self._invoice_repo.get_by_id_and_organization_id(id, organization_id)
        if invoice is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Factura no encontrada")
        return invoice

    # -- Calculo de consumo -------------------------------------------------------

    async def build_period_items(
        self, organization_id: uuid.UUID, period_start: datetime, period_end: datetime
    ) -> list[InvoiceItemInput]:
        """
        Desglose detallado de consumo por campaña para el periodo [period_start, period_end),
        listo para pasar como `items` a create_or_skip. Una fila por campaña enviada en el
        periodo, con su cantidad de mensajes y el costo real (suma de los precios snapshot
        de cada envio, no precio_unitario * cantidad, ya que el precio del canal puede haber
        cambiado durante el periodo).
        """
        usage = await self._contact_repo.get_billing_usage(organization_id, period_start, period_end)
        return [
            InvoiceItemInput(
                campaign_id=row.campaign_id,
                campaign_name=row.campaign_name,
                channel_id=row.channel_id,
                channel_name=row.channel_name,
                base_currency=row.currency,
                quantity=row.quantity,
                subtotal_base=row.subtotal,
            )
            for row in usage
        ]

    # -- Creacion ---------------------------------------------------------------

    async def create_or_skip(self, params: CreateInvoiceParams) -> InvoiceModel | None:
        existing = await self._invoice_repo.get_by_period(
            params.organization_id, params.period_year, params.period_month
        )
        if existing is not None:
            logger.info(
                "[billing] factura ya existe | org=%s periodo=%s-%s",
                params.organization_id, params.period_year, params.period_month,
            )
            return None

        tax_enabled = os.getenv("BILLING_TAX_ENABLED") == "true"
        tax_type = (os.getenv("BILLING_TAX_TYPE") or "IVA") if tax_enabled else "NONE"
        tax_rate = Decimal(os.getenv("BILLING_TAX_RATE") or "0.19") if tax_enabled else Decimal("0")

        subtotal_usd = sum((item.subtotal_base for item in params.items), Decimal("0"))
        subtotal_cop = Decimal(_round_pesos(subtotal_usd * params.exchange_rate))
        tax_amount_cop = Decimal(_round_pesos(subtotal_cop * tax_rate))
        total_cop = subtotal_cop + tax_amount_cop

        payment_due_days = int(os.getenv("BILLING_PAYMENT_DUE_DAYS") or "10")
        block_after_days = int(os.getenv("BILLING_BLOCK_AFTER_DAYS") or "20")

        now = datetime.now(timezone.utc)
        due_at = now + timedelta(days=payment_due_days)
        block_at = now + timedelta(days=block_after_days)

        is_zero = total_cop == 0
        invoice_status = InvoiceStatus.CANCELLED if is_zero else InvoiceStatus.ISSUED

        invoice = InvoiceModel(
            organization_id=params.organization_id,
            period_year=params.period_year,
            period_month=params.period_month,
            base_currency="USD",
            billing_currency="COP",
            exchange_rate=params.exchange_rate,
            subtotal_base_amount=subtotal_usd,
            subtotal_billing_amount=subtotal_cop,
            tax_type=tax_type,
            tax_rate=tax_rate,
            tax_amount=tax_amount_cop,
            total_amount=total_cop,
            status=invoice_status,
            issued_at=None if is_zero else now,
            due_at=None if is_zero else due_at,
            block_at=None if is_zero else block_at,
            items=[
                InvoiceItemModel(
                    campaign_id=item.campaign_id,
                    campaign_name=item.campaign_name,
                    channel_id=item.channel_id,
                    channel_name=item.channel_name,
                    base_currency=item.base_currency,
                    unit_price_base=(item.subtotal_base / item.quantity) if item.quantity else Decimal("0"),
                    quantity=item.quantity,
                    subtotal_base=item.subtotal_base,
                )
                for item in params.items
            ],
        )
        result = await self._invoice_repo.add(invoice)
        logger.info(
            "[billing] factura creada | id=%s org=%s periodo=%s-%s total=%s",
            result.id, params.organization_id, params.period_year, params.period_month, total_cop,
        )
        return result

    # -- Transiciones de estado --------------------------------------------------

    async def run_overdue_transitions(self) -> None:
        blocking_enabled = os.getenv("BILLING_BLOCKING_ENABLED") != "false"
        now = datetime.now(timezone.utc)

        await self._invoice_repo.mark_overdue(now)
        if blocking_enabled:
            await self._invoice_repo.mark_blocked(now)

        logger.info("[billing] transiciones overdue/blocked aplicadas")

    # -- Enlace de pago -----------------------------------------------------------

    async def create_or_reuse_payment_link(
        self, invoice_id: uuid.UUID, organization_id: uuid.UUID
    ) -> PaymentLinkResponse:
        invoice = await self.get_invoice(invoice_id, organization_id)

        if invoice.status in (InvoiceStatus.PAID, InvoiceStatus.CANCELLED):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"La factura ya esta {invoice.status.value}")

        amount = _round_pesos(invoice.total_amount)
        currency = "COP"
        description = f"Factura {invoice.period_year}-{invoice.period_month:02d}"

        latest_attempt = await self._attempt_repo.get_latest_by_invoice_id(invoice.id)
        is_recent = (
            latest_attempt is not None
            and datetime.now(timezone.utc) - latest_attempt.created_at < _ATTEMPT_TTL
        )

        if (
            latest_attempt is not None
            and is_attempt_reusable(latest_attempt.status)
            and latest_attempt.bold_reference
            and is_recent
        ):
            integrity_signature = generate_integrity_hash(latest_attempt.bold_reference, amount, currency)
            return self._payment_link_payload(
                order_id=latest_attempt.bold_reference,
                amount=amount,
                currency=currency,
                integrity_signature=integrity_signature,
                description=description,
                tax_type=invoice.tax_type,
                attempt_id=latest_attempt.id,
                reused=True,
            )

        attempt_number = (latest_attempt.attempt_number + 1) if latest_attempt else 1
        short_id = invoice_id.hex[:8].upper()
        ts = _to_base36(int(datetime.now(timezone.utc).timestamp() * 1000))
        bold_ref = f"INV-{short_id}-{attempt_number}-{ts}"[:60]

        integrity_signature = generate_integrity_hash(bold_ref, amount, currency)

        attempt = await self._attempt_repo.add(
            PaymentAttemptModel(
                invoice_id=invoice_id,
                attempt_number=attempt_number,
                bold_reference=bold_ref,
                status=PaymentAttemptStatus.ACTIVE,
            )
        )

        transition = attempt_status_to_invoice_transition(attempt.status, invoice.status)
        if transition is not None:
            invoice.status = transition
            await self._invoice_repo.update(invoice)

        return self._payment_link_payload(
            order_id=bold_ref,
            amount=amount,
            currency=currency,
            integrity_signature=integrity_signature,
            description=description,
            tax_type=invoice.tax_type,
            attempt_id=attempt.id,
            reused=False,
        )

    def _payment_link_payload(
        self,
        order_id: str,
        amount: int,
        currency: str,
        integrity_signature: str,
        description: str,
        tax_type: str,
        attempt_id: uuid.UUID,
        reused: bool,
    ) -> PaymentLinkResponse:
        return PaymentLinkResponse(
            order_id=order_id,
            amount=amount,
            currency=currency,
            integrity_signature=integrity_signature,
            description=description,
            tax_type=tax_type,
            attempt_id=attempt_id,
            reused=reused,
            api_key=get_or_throw("BOLD_API_KEY"),
            redirection_url=get_or_throw("BOLD_REDIRECTION_URL"),
        )

    async def sync_invoice_payment_status(self, invoice_id: uuid.UUID, organization_id: uuid.UUID) -> InvoiceModel:
        # El boton de pagos solo actualiza el estado via webhook (SALE_APPROVED);
        # no se hacen llamadas a la API de Bold desde el backend.
        return await self.get_invoice(invoice_id, organization_id)

    async def handle_webhook_paid(self, bold_reference: str, payload: dict[str, Any]) -> None:
        if payload.get("type") and payload["type"] != "SALE_APPROVED":
            return

        attempt = await self._attempt_repo.get_by_bold_reference(bold_reference)
        if attempt is None:
            logger.warning("[billing] sin intento para referencia Bold %s", bold_reference)
            return

        if attempt.status == PaymentAttemptStatus.PAID:
            return

        attempt.status = PaymentAttemptStatus.PAID
        attempt.bold_payload = payload
        await self._attempt_repo.update(attempt)

        invoice = await self._invoice_repo.get_by_id(attempt.invoice_id)
        if invoice is not None and invoice.status != InvoiceStatus.PAID:
            invoice.status = InvoiceStatus.PAID
            invoice.paid_at = datetime.now(timezone.utc)
            await self._invoice_repo.update(invoice)
