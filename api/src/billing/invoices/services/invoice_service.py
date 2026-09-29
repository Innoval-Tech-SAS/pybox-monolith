import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status
from httpx import HTTPStatusError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config.logger import logger
from billing.gateways.resolver import PaymentGatewayResolver
from billing.invoices.constants.billing_constants import ATTEMPT_TTL, billing_config
from billing.invoices.enums.invoice_enums import InvoiceStatus, PaymentAttemptStatus, PaymentProvider
from billing.invoices.models.invoice_model import InvoiceModel
from billing.invoices.models.invoice_item_model import InvoiceItemModel
from billing.invoices.models.payment_attempt_model import InvoicePaymentAttemptModel
from billing.invoices.repository.invoice_repository import InvoiceRepository
from billing.invoices.repository.payment_attempt_repository import InvoicePaymentAttemptRepository
from billing.invoices.schemas.invoice_params_schemas import CreateInvoiceParams, InvoiceItemInput
from billing.invoices.schemas.invoice_schemas import (
    AdminInvoiceResponse,
    AdminListInvoicesResponse,
    InvoiceResponse,
    ListInvoicesResponse,
    PaymentLinkResponse,
)
from billing.invoices.status_transitions import attempt_status_to_invoice_transition, is_attempt_reusable
from billing.invoices.utils.invoice_utils import round_pesos, to_base36
from billing.mercadopago.services.mercadopago_client import MercadoPagoClient
from billing.mercadopago.enums.mercadopago_enums import MercadoPagoOrderStatus
from billing.mercadopago.utils.mercadopago_credentials import resolve_credentials_for_country
from billing.mercadopago.utils.mercadopago_status_mapper import mercadopago_order_status_to_attempt_status
from identity.organizations.repository.organization_repository import OrganizationRepository
from messaging.contacts.repository.contact_repository import ContactRepository


class InvoiceService:
    def __init__(
        self,
        session: AsyncSession,
        invoice_repo: InvoiceRepository,
        attempt_repo: InvoicePaymentAttemptRepository,
        contact_repo: ContactRepository,
        organization_repo: OrganizationRepository,
        gateway_resolver: PaymentGatewayResolver,
    ):
        self._session = session
        self._invoice_repo = invoice_repo
        self._attempt_repo = attempt_repo
        self._contact_repo = contact_repo
        self._organization_repo = organization_repo
        self._gateway_resolver = gateway_resolver
        self._mp_client = MercadoPagoClient()

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

    # -- Consulta admin (cross-organizacion, solo lectura) ------------------------

    async def get_invoice_admin(self, id: uuid.UUID) -> AdminInvoiceResponse:
        row = await self._invoice_repo.get_by_id_with_organization_name(id)
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Factura no encontrada")
        invoice, organization_name = row
        return AdminInvoiceResponse(
            **InvoiceResponse.model_validate(invoice).model_dump(),
            organization_name=organization_name,
        )

    async def list_invoices_admin(
        self, page: int, limit: int, organization_id: uuid.UUID | None = None
    ) -> AdminListInvoicesResponse:
        rows, total = await self._invoice_repo.list_all_with_organization_name(page, limit, organization_id)
        invoices = [
            AdminInvoiceResponse(
                **InvoiceResponse.model_validate(invoice).model_dump(),
                organization_name=organization_name,
            )
            for invoice, organization_name in rows
        ]
        return AdminListInvoicesResponse(
            invoices=invoices,
            total=total,
            page=page,
            limit=limit,
            total_pages=-(-total // limit) if limit else 0,
        )

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

        tax_enabled = billing_config.tax_enabled
        tax_type = billing_config.tax_type if tax_enabled else "NONE"
        tax_rate = billing_config.tax_rate if tax_enabled else Decimal("0")

        subtotal_usd = sum((item.subtotal_base for item in params.items), Decimal("0"))
        subtotal_billing = Decimal(round_pesos(subtotal_usd * params.exchange_rate))
        tax_amount_billing = Decimal(round_pesos(subtotal_billing * tax_rate))
        total_billing = subtotal_billing + tax_amount_billing

        now = datetime.now(timezone.utc)
        due_at = now + timedelta(days=billing_config.payment_due_days)
        block_at = now + timedelta(days=billing_config.block_after_days)

        is_zero = total_billing == 0
        invoice_status = InvoiceStatus.CANCELLED if is_zero else InvoiceStatus.ISSUED

        invoice = InvoiceModel(
            organization_id=params.organization_id,
            period_year=params.period_year,
            period_month=params.period_month,
            base_currency="USD",
            billing_currency=params.billing_currency,
            exchange_rate=params.exchange_rate,
            subtotal_base_amount=subtotal_usd,
            subtotal_billing_amount=subtotal_billing,
            tax_type=tax_type,
            tax_rate=tax_rate,
            tax_amount=tax_amount_billing,
            total_amount=total_billing,
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
            "[billing] factura creada | id=%s org=%s periodo=%s-%s moneda=%s total=%s",
            result.id, params.organization_id, params.period_year, params.period_month,
            params.billing_currency, total_billing,
        )
        return result

    # -- Transiciones de estado --------------------------------------------------

    async def run_overdue_transitions(self) -> None:
        now = datetime.now(timezone.utc)

        await self._invoice_repo.mark_overdue(now)
        if billing_config.blocking_enabled:
            await self._invoice_repo.mark_blocked(now)

        logger.info("[billing] transiciones overdue/blocked aplicadas")

    # -- Enlace de pago -----------------------------------------------------------

    async def create_or_reuse_payment_link(
        self, invoice_id: uuid.UUID, organization_id: uuid.UUID, payer_email: str
    ) -> PaymentLinkResponse:
        invoice = await self.get_invoice(invoice_id, organization_id)

        if invoice.status in (InvoiceStatus.PAID, InvoiceStatus.CANCELLED):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"La factura ya esta {invoice.status.value}")

        org = await self._organization_repo.get_by_id(organization_id)
        gateway = await self._gateway_resolver.get_for_country(org.country if org else None, self._session)

        amount = round_pesos(invoice.total_amount)
        currency = invoice.billing_currency
        description = f"Factura {invoice.period_year}-{invoice.period_month:02d}"

        latest_attempt = await self._attempt_repo.get_latest_by_invoice_id(invoice.id)
        is_recent = (
            latest_attempt is not None
            and datetime.now(timezone.utc) - latest_attempt.created_at < ATTEMPT_TTL
        )

        if (
            latest_attempt is not None
            and is_attempt_reusable(latest_attempt.status)
            and latest_attempt.provider_reference
            and latest_attempt.provider == gateway.name
            and is_recent
        ):
            return self._payment_link_payload(
                provider=gateway.name,
                order_id=latest_attempt.provider_reference,
                amount=amount,
                currency=currency,
                description=description,
                tax_type=invoice.tax_type,
                attempt_id=latest_attempt.id,
                reused=True,
                provider_payload=latest_attempt.provider_payload or {},
            )

        attempt_number = (latest_attempt.attempt_number + 1) if latest_attempt else 1
        short_id = invoice_id.hex[:8].upper()
        ts = to_base36(int(datetime.now(timezone.utc).timestamp() * 1000))
        reference = f"INV-{short_id}-{attempt_number}-{ts}"[:60]

        link = await gateway.create_payment_link(
            reference, amount, currency, description, invoice.tax_type, invoice.tax_rate, payer_email
        )

        attempt = await self._attempt_repo.add(
            InvoicePaymentAttemptModel(
                invoice_id=invoice_id,
                attempt_number=attempt_number,
                provider=PaymentProvider(gateway.name),
                provider_reference=link.reference,
                provider_link_id=link.provider_link_id,
                payment_url=link.payment_url,
                status=PaymentAttemptStatus.ACTIVE,
                expected_amount=amount,
                provider_payload=link.provider_payload,
            )
        )

        transition = attempt_status_to_invoice_transition(attempt.status, invoice.status)
        if transition is not None:
            invoice.status = transition
            await self._invoice_repo.update(invoice)

        return self._payment_link_payload(
            provider=gateway.name,
            order_id=link.reference,
            amount=amount,
            currency=currency,
            description=description,
            tax_type=invoice.tax_type,
            attempt_id=attempt.id,
            reused=False,
            provider_payload=link.provider_payload,
        )

    def _payment_link_payload(
        self,
        provider: str,
        order_id: str,
        amount: int,
        currency: str,
        description: str,
        tax_type: str,
        attempt_id: uuid.UUID,
        reused: bool,
        provider_payload: dict[str, Any],
    ) -> PaymentLinkResponse:
        return PaymentLinkResponse(
            provider=provider,
            order_id=order_id,
            amount=amount,
            currency=currency,
            description=description,
            tax_type=tax_type,
            attempt_id=attempt_id,
            reused=reused,
            provider_payload=provider_payload,
        )

    async def sync_invoice_payment_status(self, invoice_id: uuid.UUID, organization_id: uuid.UUID) -> InvoiceModel:
        # El estado solo se actualiza via webhook del proveedor; el backend no
        # consulta proactivamente el estado de pago ante el proveedor.
        return await self.get_invoice(invoice_id, organization_id)

    async def mark_attempt_paid(
        self,
        provider: str,
        reference: str,
        reported_amount: Decimal | None,
        payload: dict[str, Any],
    ) -> None:
        """
        Punto de entrada para webhooks de proveedores que confirman el pago por la
        referencia que nosotros generamos (ej. Bold, que la devuelve en data.metadata.reference).
        """
        # for_update=True: dos entregas concurrentes del mismo webhook (reintento típico
        # de los proveedores) no deben poder pasar ambas el check de "ya está pagado" —
        # la segunda espera el lock y lee el estado ya actualizado por la primera.
        attempt = await self._attempt_repo.get_by_provider_reference(reference, for_update=True)
        if attempt is None:
            logger.warning("[billing] sin intento para referencia %s | proveedor=%s", reference, provider)
            return
        await self._mark_attempt_paid(provider, attempt, reported_amount, payload)

    async def sync_attempt_status_by_link_id(
        self,
        provider: str,
        link_id: str,
        status: PaymentAttemptStatus,
        reported_amount: Decimal | None,
        payload: dict[str, Any],
    ) -> None:
        """
        Punto de entrada para webhooks de proveedores que solo identifican el recurso por su
        propio id (ej. Mercado Pago Orders API, que entrega `data.id` en vez de nuestra referencia).
        A diferencia de `mark_attempt_paid`, aqui tambien se propagan estados intermedios
        (PROCESSING, EXPIRED, REJECTED, CANCELLED), no solo el pago aprobado.
        """
        # Mismo motivo que en mark_attempt_paid: lock de fila para que dos webhooks
        # concurrentes no pisen la transición de estado.
        attempt = await self._attempt_repo.get_by_provider_link_id(link_id, for_update=True)
        if attempt is None:
            logger.warning("[billing] sin intento para link_id %s | proveedor=%s", link_id, provider)
            return
        await self._apply_attempt_status(provider, attempt, status, reported_amount, payload)

    async def charge_mercadopago_attempt(
        self,
        invoice_id: uuid.UUID,
        organization_id: uuid.UUID,
        attempt_id: uuid.UUID,
        token: str,
        payment_method_id: str,
        payment_type_id: str,
        installments: int,
    ) -> InvoiceModel:
        """
        Modo manual de la Orders API: el token de tarjeta ya fue generado en el frontend
        via Secure Fields (nunca pasa la tarjeta cruda por este backend). Aqui se agrega
        la transaccion a la Order y se procesa de inmediato; el estado final tambien
        llegara por webhook, esta llamada solo evita que el usuario tenga que esperar
        a que llegue para ver el resultado en pantalla.
        """
        invoice = await self.get_invoice(invoice_id, organization_id)
        attempt = next((a for a in invoice.attempts if a.id == attempt_id), None)
        if attempt is None or attempt.provider != PaymentProvider.MERCADO_PAGO or not attempt.provider_link_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Intento de pago de Mercado Pago no encontrado")
        if attempt.status == PaymentAttemptStatus.PAID:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Este intento ya fue pagado")

        org = await self._organization_repo.get_by_id(organization_id)
        credentials = await resolve_credentials_for_country(self._session, org.country if org else None)
        if credentials is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Mercado Pago no esta configurado para este pais")

        # La Order de MP es de un solo uso: una vez que sale de `created` (procesada,
        # fallida, cancelada o expirada) ya no admite otro `/process` (MP responde 400
        # invalid_order_mode_for_operation). Si el intento se reintenta sobre una Order ya
        # terminal, se mapea su estado al intento (failed -> REJECTED) y se corta aqui: eso
        # lo vuelve no-reutilizable (ver is_attempt_reusable) para que el proximo intento
        # genere una Order nueva, en vez de reprocesar la muerta y explotar en 500.
        order = await self._mp_client.get_order(credentials.access_token, attempt.provider_link_id)
        if order.get("status", "") != MercadoPagoOrderStatus.CREATED.value:
            await self._sync_mercadopago_order_to_attempt(attempt, order)
            return await self.get_invoice(invoice_id, organization_id)

        # La Order solo acepta una transaccion: si un intento anterior ya la agrego pero se
        # cayo antes de procesar (ej. error de red, restart), reintentar `add_transaction`
        # responde 409 sin importar la Idempotency-Key. Solo se agrega si todavia no tiene.
        has_transaction = bool((order.get("transactions") or {}).get("payments"))
        if not has_transaction:
            await self._mp_client.add_transaction(
                credentials.access_token,
                attempt.provider_link_id,
                attempt.expected_amount or 0,
                token,
                payment_method_id,
                payment_type_id,
                installments,
                str(uuid.uuid4()),
            )

        try:
            order = await self._mp_client.process_order(
                credentials.access_token, attempt.provider_link_id, str(uuid.uuid4())
            )
        except HTTPStatusError:
            # MP puede rechazar el cobro (ej. invalid_users_involved, fondos, issuer) y
            # devolverlo como error HTTP en vez de una Order con status "failed". La Order
            # igual queda en su estado terminal en MP, asi que se re-lee: si ya salio de
            # `created` fue un rechazo legitimo -> se mapea a REJECTED y no se propaga el
            # error; si sigue `created` fue un fallo real de la request y se re-lanza.
            order = await self._mp_client.get_order(credentials.access_token, attempt.provider_link_id)
            if order.get("status", "") == MercadoPagoOrderStatus.CREATED.value:
                raise

        await self._sync_mercadopago_order_to_attempt(attempt, order)
        return await self.get_invoice(invoice_id, organization_id)

    async def _sync_mercadopago_order_to_attempt(
        self, attempt: InvoicePaymentAttemptModel, order: dict[str, Any]
    ) -> None:
        """
        Mapea el estado de una Order de MP al intento (failed -> REJECTED, processed ->
        PAID, etc.) y lo persiste. Los estados sin transicion de intento
        (REFUNDED/CHARGED_BACK/desconocidos) se ignoran: son casos que maneja el webhook.
        """
        attempt_status = mercadopago_order_status_to_attempt_status(order.get("status", ""))
        if attempt_status is None:
            return
        payments = (order.get("transactions") or {}).get("payments") or []
        reported_amount = Decimal(str(payments[0]["amount"])) if payments else None
        await self._apply_attempt_status("MERCADO_PAGO", attempt, attempt_status, reported_amount, order)

    async def _apply_attempt_status(
        self,
        provider: str,
        attempt: InvoicePaymentAttemptModel,
        status: PaymentAttemptStatus,
        reported_amount: Decimal | None,
        payload: dict[str, Any],
    ) -> None:
        if status == PaymentAttemptStatus.PAID:
            await self._mark_attempt_paid(provider, attempt, reported_amount, payload)
            return

        if attempt.status == status or attempt.status == PaymentAttemptStatus.PAID:
            return

        attempt.status = status
        attempt.provider_payload = payload
        await self._attempt_repo.update(attempt)

        invoice = await self._invoice_repo.get_by_id(attempt.invoice_id)
        if invoice is not None:
            transition = attempt_status_to_invoice_transition(status, invoice.status)
            if transition is not None:
                invoice.status = transition
                await self._invoice_repo.update(invoice)

    async def _mark_attempt_paid(
        self,
        provider: str,
        attempt: InvoicePaymentAttemptModel,
        reported_amount: Decimal | None,
        payload: dict[str, Any],
    ) -> None:
        if attempt.status == PaymentAttemptStatus.PAID:
            return

        if attempt.expected_amount is not None and reported_amount is not None:
            try:
                reported_amount_int = round_pesos(reported_amount)
            except (TypeError, ValueError, ArithmeticError):
                reported_amount_int = None
            if reported_amount_int != attempt.expected_amount:
                logger.warning(
                    "[billing] monto del webhook no coincide | proveedor=%s id=%s esperado=%s reportado=%s",
                    provider, attempt.id, attempt.expected_amount, reported_amount,
                )
                return

        attempt.status = PaymentAttemptStatus.PAID
        attempt.provider_payload = payload
        await self._attempt_repo.update(attempt)

        invoice = await self._invoice_repo.get_by_id(attempt.invoice_id)
        if invoice is not None and invoice.status != InvoiceStatus.PAID:
            invoice.status = InvoiceStatus.PAID
            invoice.paid_at = datetime.now(timezone.utc)
            await self._invoice_repo.update(invoice)
