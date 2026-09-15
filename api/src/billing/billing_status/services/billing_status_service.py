import uuid
from datetime import datetime, timezone

from billing.billing_status.enums.billing_status_enums import TenantBillingLockStatus
from billing.billing_status.schemas.billing_status_schemas import TenantBillingStatusResponse
from billing.invoices.constants.billing_constants import billing_config
from billing.invoices.enums.invoice_enums import InvoiceStatus
from billing.invoices.repository.invoice_repository import InvoiceRepository

_DUE_SOON_THRESHOLD_DAYS = 3


class BillingStatusService:
    def __init__(self, invoice_repo: InvoiceRepository):
        self._invoice_repo = invoice_repo

    async def is_blocked(self, organization_id: uuid.UUID) -> bool:
        """True si la organizacion tiene alguna factura vencida sin pagar.

        Es la unica fuente de verdad del corte de envios: se consulta desde los tres
        flujos de envio (manual, activacion de campana y tick automatico) antes de
        resolver el canal, de modo que el bloqueo aplica a todos los canales por igual.

        Con billing_config.blocking_enabled en "false" nunca corta, aunque haya facturas
        vencidas: es la valvula de escape para reanudar envios sin tocar la base de datos.
        """
        if not billing_config.blocking_enabled:
            return False

        blocking_invoice = await self._invoice_repo.get_oldest_unpaid_due(
            organization_id, datetime.now(timezone.utc)
        )
        return blocking_invoice is not None

    async def get_status(self, organization_id: uuid.UUID) -> TenantBillingStatusResponse:
        overdue_invoice = await self._invoice_repo.get_oldest_unpaid_due(
            organization_id, datetime.now(timezone.utc)
        )
        if overdue_invoice is not None:
            # Sin bloqueo activo la factura sigue vencida y hay que cobrarla, pero no se
            # anuncia como bloqueo porque los envios no se estan cortando.
            if not billing_config.blocking_enabled:
                return TenantBillingStatusResponse(
                    lock_status=TenantBillingLockStatus.PAYMENT_REQUIRED,
                    active_invoice_id=overdue_invoice.id,
                    message="Factura vencida sin pagar. Realiza el pago para ponerte al dia.",
                )
            return TenantBillingStatusResponse(
                lock_status=TenantBillingLockStatus.BLOCKED,
                active_invoice_id=overdue_invoice.id,
                message="Envios bloqueados por factura vencida sin pagar. Realiza el pago para reanudarlos.",
            )

        # Llegados aqui no hay ninguna factura vencida: solo quedan facturas por vencer.
        open_invoice = await self._invoice_repo.get_open_by_organization_id(organization_id)
        if open_invoice is None:
            return TenantBillingStatusResponse(lock_status=TenantBillingLockStatus.NONE)

        if open_invoice.status == InvoiceStatus.PAYMENT_PENDING:
            return TenantBillingStatusResponse(
                lock_status=TenantBillingLockStatus.PAYMENT_REQUIRED,
                active_invoice_id=open_invoice.id,
                message="El pago esta siendo procesado.",
            )

        if open_invoice.status == InvoiceStatus.ISSUED:
            if open_invoice.due_at is None:
                return TenantBillingStatusResponse(
                    lock_status=TenantBillingLockStatus.WARNING, active_invoice_id=open_invoice.id
                )

            days_until_due = (open_invoice.due_at - datetime.now(timezone.utc)).days
            if days_until_due <= _DUE_SOON_THRESHOLD_DAYS:
                return TenantBillingStatusResponse(
                    lock_status=TenantBillingLockStatus.PAYMENT_REQUIRED,
                    active_invoice_id=open_invoice.id,
                    message=f"Factura vence en {days_until_due} dia(s).",
                )
            return TenantBillingStatusResponse(
                lock_status=TenantBillingLockStatus.WARNING,
                active_invoice_id=open_invoice.id,
                message=f"Factura vence el {open_invoice.due_at.date().isoformat()}.",
            )

        return TenantBillingStatusResponse(lock_status=TenantBillingLockStatus.NONE)
