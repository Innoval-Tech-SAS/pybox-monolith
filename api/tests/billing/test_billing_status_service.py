"""BillingStatusService probado como unidad: InvoiceRepository mockeado con AsyncMock
(sin pytest-mock). `billing_config` es un singleton mutable a nivel de modulo
(billing/invoices/constants/billing_constants.py) -- se parcha con
`monkeypatch.setattr` para no depender de variables de entorno reales y revertir
solo al final del test."""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

from billing.billing_status.enums.billing_status_enums import TenantBillingLockStatus
from billing.billing_status.services.billing_status_service import BillingStatusService
from billing.invoices.constants.billing_constants import billing_config
from billing.invoices.enums.invoice_enums import InvoiceStatus


def make_service():
    invoice_repo = AsyncMock()
    return BillingStatusService(invoice_repo), invoice_repo


def make_invoice(**overrides):
    defaults = dict(id=uuid.uuid4(), status=InvoiceStatus.ISSUED, due_at=None)
    defaults.update(overrides)
    return MagicMock(**defaults)


class TestIsBlocked:
    async def test_blocking_disabled_returns_false_even_with_overdue_invoice(
        self, monkeypatch
    ):
        monkeypatch.setattr(billing_config, "blocking_enabled", False)
        service, invoice_repo = make_service()
        invoice_repo.get_oldest_unpaid_due = AsyncMock(
            return_value=make_invoice(status=InvoiceStatus.OVERDUE)
        )

        assert await service.is_blocked(uuid.uuid4()) is False
        # La valvula de escape corta antes de consultar la DB.
        invoice_repo.get_oldest_unpaid_due.assert_not_awaited()

    async def test_blocking_enabled_with_overdue_invoice_returns_true(
        self, monkeypatch
    ):
        monkeypatch.setattr(billing_config, "blocking_enabled", True)
        service, invoice_repo = make_service()
        invoice_repo.get_oldest_unpaid_due = AsyncMock(
            return_value=make_invoice(status=InvoiceStatus.OVERDUE)
        )

        assert await service.is_blocked(uuid.uuid4()) is True

    async def test_blocking_enabled_with_no_overdue_invoice_returns_false(
        self, monkeypatch
    ):
        monkeypatch.setattr(billing_config, "blocking_enabled", True)
        service, invoice_repo = make_service()
        invoice_repo.get_oldest_unpaid_due = AsyncMock(return_value=None)

        assert await service.is_blocked(uuid.uuid4()) is False


class TestGetStatus:
    async def test_issued_due_in_two_days_is_payment_required(self, monkeypatch):
        monkeypatch.setattr(billing_config, "blocking_enabled", True)
        service, invoice_repo = make_service()
        invoice_repo.get_oldest_unpaid_due = AsyncMock(return_value=None)
        invoice = make_invoice(
            status=InvoiceStatus.ISSUED,
            due_at=datetime.now(timezone.utc) + timedelta(days=2),
        )
        invoice_repo.get_open_by_organization_id = AsyncMock(return_value=invoice)

        result = await service.get_status(uuid.uuid4())

        assert result.lock_status == TenantBillingLockStatus.PAYMENT_REQUIRED
        assert result.active_invoice_id == invoice.id

    async def test_issued_due_in_ten_days_is_warning(self, monkeypatch):
        monkeypatch.setattr(billing_config, "blocking_enabled", True)
        service, invoice_repo = make_service()
        invoice_repo.get_oldest_unpaid_due = AsyncMock(return_value=None)
        invoice = make_invoice(
            status=InvoiceStatus.ISSUED,
            due_at=datetime.now(timezone.utc) + timedelta(days=10),
        )
        invoice_repo.get_open_by_organization_id = AsyncMock(return_value=invoice)

        result = await service.get_status(uuid.uuid4())

        assert result.lock_status == TenantBillingLockStatus.WARNING
        assert result.active_invoice_id == invoice.id

    async def test_no_open_invoice_returns_none_status(self, monkeypatch):
        monkeypatch.setattr(billing_config, "blocking_enabled", True)
        service, invoice_repo = make_service()
        invoice_repo.get_oldest_unpaid_due = AsyncMock(return_value=None)
        invoice_repo.get_open_by_organization_id = AsyncMock(return_value=None)

        result = await service.get_status(uuid.uuid4())

        assert result.lock_status == TenantBillingLockStatus.NONE
        assert result.active_invoice_id is None

    async def test_overdue_invoice_with_blocking_enabled_returns_blocked(
        self, monkeypatch
    ):
        monkeypatch.setattr(billing_config, "blocking_enabled", True)
        service, invoice_repo = make_service()
        overdue = make_invoice(status=InvoiceStatus.OVERDUE)
        invoice_repo.get_oldest_unpaid_due = AsyncMock(return_value=overdue)

        result = await service.get_status(uuid.uuid4())

        assert result.lock_status == TenantBillingLockStatus.BLOCKED
        assert result.active_invoice_id == overdue.id

    async def test_overdue_invoice_with_blocking_disabled_returns_payment_required_not_blocked(
        self, monkeypatch
    ):
        monkeypatch.setattr(billing_config, "blocking_enabled", False)
        service, invoice_repo = make_service()
        overdue = make_invoice(status=InvoiceStatus.OVERDUE)
        invoice_repo.get_oldest_unpaid_due = AsyncMock(return_value=overdue)

        result = await service.get_status(uuid.uuid4())

        assert result.lock_status == TenantBillingLockStatus.PAYMENT_REQUIRED
        assert result.active_invoice_id == overdue.id
