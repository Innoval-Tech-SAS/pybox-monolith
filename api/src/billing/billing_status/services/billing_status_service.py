import uuid
from datetime import datetime, timezone

from billing.billing_status.enums.billing_status_enums import TenantBillingLockStatus
from billing.billing_status.schemas.billing_status_schemas import TenantBillingStatusResponse
from billing.invoices.enums.invoice_enums import InvoiceStatus
from billing.invoices.repository.invoice_repository import InvoiceRepository

_DUE_SOON_THRESHOLD_DAYS = 3


class BillingStatusService:
    def __init__(self, invoice_repo: InvoiceRepository):
        self._invoice_repo = invoice_repo

    async def is_blocked(self, organization_id: uuid.UUID) -> bool:
        result = await self.get_status(organization_id)
        return result.lock_status == TenantBillingLockStatus.BLOCKED

    async def get_status(self, organization_id: uuid.UUID) -> TenantBillingStatusResponse:
        open_invoice = await self._invoice_repo.get_open_by_organization_id(organization_id)
        if open_invoice is None:
            return TenantBillingStatusResponse(lock_status=TenantBillingLockStatus.NONE)

        if open_invoice.status == InvoiceStatus.BLOCKED:
            return TenantBillingStatusResponse(
                lock_status=TenantBillingLockStatus.BLOCKED,
                active_invoice_id=open_invoice.id,
                message="Cuenta bloqueada por factura impaga. Realiza el pago para restablecer el acceso.",
            )

        if open_invoice.status == InvoiceStatus.OVERDUE:
            return TenantBillingStatusResponse(
                lock_status=TenantBillingLockStatus.PAYMENT_REQUIRED,
                active_invoice_id=open_invoice.id,
                message="Factura vencida. El acceso se bloqueara pronto.",
            )

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
