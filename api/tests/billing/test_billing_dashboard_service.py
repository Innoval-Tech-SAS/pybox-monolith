"""BillingDashboardService probado como unidad: InvoiceRepository mockeado con
AsyncMock (sin pytest-mock). Foco: los calculos derivados (collection_rate, relleno de
meses sin facturacion) no deben reventar con datos vacios ni dar division por cero."""

from decimal import Decimal
from unittest.mock import AsyncMock

from billing.billing_dashboard.services.billing_dashboard_service import BillingDashboardService
from billing.invoices.enums.invoice_enums import InvoiceStatus, PaymentProvider


def make_service():
    invoice_repo = AsyncMock()
    return BillingDashboardService(invoice_repo), invoice_repo


class TestGetSummary:
    async def test_collection_rate_is_percentage_of_paid_over_total(self):
        service, invoice_repo = make_service()
        invoice_repo.get_revenue_for_period = AsyncMock(return_value=Decimal("1000"))
        invoice_repo.get_overdue_amount = AsyncMock(return_value=Decimal("50"))
        invoice_repo.count_billed_organizations = AsyncMock(return_value=4)
        invoice_repo.get_status_breakdown = AsyncMock(
            return_value=[
                (InvoiceStatus.PAID, 3, Decimal("750")),
                (InvoiceStatus.ISSUED, 1, Decimal("250")),
            ]
        )

        result = await service.get_summary()

        assert result.current_month_revenue == Decimal("1000")
        assert result.overdue_amount == Decimal("50")
        assert result.billed_organizations_count == 4
        assert result.collection_rate == 75.0

    async def test_no_invoices_in_period_gives_zero_collection_rate_not_division_error(self):
        service, invoice_repo = make_service()
        invoice_repo.get_revenue_for_period = AsyncMock(return_value=Decimal("0"))
        invoice_repo.get_overdue_amount = AsyncMock(return_value=Decimal("0"))
        invoice_repo.count_billed_organizations = AsyncMock(return_value=0)
        invoice_repo.get_status_breakdown = AsyncMock(return_value=[])

        result = await service.get_summary()

        assert result.collection_rate == 0.0

    async def test_collection_rate_rounds_to_one_decimal(self):
        service, invoice_repo = make_service()
        invoice_repo.get_revenue_for_period = AsyncMock(return_value=Decimal("0"))
        invoice_repo.get_overdue_amount = AsyncMock(return_value=Decimal("0"))
        invoice_repo.count_billed_organizations = AsyncMock(return_value=0)
        invoice_repo.get_status_breakdown = AsyncMock(
            return_value=[
                (InvoiceStatus.PAID, 1, Decimal("1")),
                (InvoiceStatus.ISSUED, 2, Decimal("2")),
            ]
        )

        result = await service.get_summary()

        assert result.collection_rate == 33.3


class TestGetInvoiceStatusBreakdown:
    async def test_maps_repository_rows_to_items(self):
        service, invoice_repo = make_service()
        invoice_repo.get_status_breakdown = AsyncMock(
            return_value=[(InvoiceStatus.OVERDUE, 2, Decimal("500"))]
        )

        result = await service.get_invoice_status_breakdown()

        assert len(result.items) == 1
        assert result.items[0].status == InvoiceStatus.OVERDUE
        assert result.items[0].count == 2
        assert result.items[0].total_amount == Decimal("500")

    async def test_empty_breakdown_returns_empty_items(self):
        service, invoice_repo = make_service()
        invoice_repo.get_status_breakdown = AsyncMock(return_value=[])

        result = await service.get_invoice_status_breakdown()

        assert result.items == []


class TestGetRevenueByChannel:
    async def test_maps_repository_rows_to_items(self):
        service, invoice_repo = make_service()
        invoice_repo.get_revenue_by_channel = AsyncMock(
            return_value=[("SMS", Decimal("300")), ("Email", Decimal("100"))]
        )

        result = await service.get_revenue_by_channel()

        assert [item.channel_name for item in result.items] == ["SMS", "Email"]
        assert [item.total_amount for item in result.items] == [Decimal("300"), Decimal("100")]

    async def test_window_is_twelve_months_back(self):
        service, invoice_repo = make_service()
        invoice_repo.get_revenue_by_channel = AsyncMock(return_value=[])

        await service.get_revenue_by_channel()

        (since_year, since_month), _kwargs = invoice_repo.get_revenue_by_channel.await_args
        # 12 meses hacia atras desde el mes actual: la diferencia de meses totales debe
        # ser exactamente 11 (incluye el mes actual como el 12avo).
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        months_back = (now.year - since_year) * 12 + (now.month - since_month)
        assert months_back == 11


class TestGetRevenueByProvider:
    async def test_maps_repository_rows_to_items(self):
        service, invoice_repo = make_service()
        invoice_repo.get_revenue_by_provider = AsyncMock(
            return_value=[(PaymentProvider.BOLD, Decimal("400")), (PaymentProvider.MERCADO_PAGO, Decimal("120"))]
        )

        result = await service.get_revenue_by_provider()

        assert [item.provider for item in result.items] == [PaymentProvider.BOLD, PaymentProvider.MERCADO_PAGO]
        assert [item.total_amount for item in result.items] == [Decimal("400"), Decimal("120")]


class TestGetMonthlyRevenue:
    async def test_fills_missing_months_with_zero_and_formats_period(self):
        from datetime import datetime, timezone

        service, invoice_repo = make_service()
        now = datetime.now(timezone.utc)
        invoice_repo.get_monthly_revenue = AsyncMock(return_value=[(now.year, now.month, Decimal("999"))])

        result = await service.get_monthly_revenue()

        assert len(result.points) == 12
        assert result.points[-1].period == f"{now.year}-{now.month:02d}"
        assert result.points[-1].total_amount == Decimal("999")
        # Todos los demas meses del rango, sin datos del repositorio, deben quedar en 0
        # en vez de faltar del listado (el frontend arma la grafica por indice fijo).
        zero_points = [p for p in result.points if p.total_amount == Decimal("0")]
        assert len(zero_points) == 11

    async def test_period_string_zero_pads_single_digit_months(self):
        from datetime import datetime, timezone

        service, invoice_repo = make_service()
        invoice_repo.get_monthly_revenue = AsyncMock(return_value=[(2026, 3, Decimal("10"))])

        result = await service.get_monthly_revenue()

        periods = [p.period for p in result.points]
        assert all(len(p) == 7 and p[4] == "-" for p in periods)
