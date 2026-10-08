"""Agregados de facturación para el dashboard: resumen, tendencia y desglose."""

from decimal import Decimal

from billing.billing_dashboard.schemas.billing_dashboard_schemas import (
    BillingSummaryResponse,
    InvoiceStatusBreakdownItem,
    InvoiceStatusBreakdownResponse,
    MonthlyRevenuePoint,
    MonthlyRevenueResponse,
    RevenueByChannelItem,
    RevenueByChannelResponse,
    RevenueByProviderItem,
    RevenueByProviderResponse,
)
from billing.billing_dashboard.utils.billing_dashboard_utils import (
    current_period,
    last_n_months,
)
from billing.invoices.enums.invoice_enums import InvoiceStatus
from billing.invoices.repository.invoice_repository import InvoiceRepository

_REVENUE_WINDOW = 12


class BillingDashboardService:
    def __init__(self, invoice_repo: InvoiceRepository):
        self._invoice_repo = invoice_repo

    async def get_summary(self) -> BillingSummaryResponse:
        year, month = current_period()

        revenue = await self._invoice_repo.get_revenue_for_period(year, month)
        overdue = await self._invoice_repo.get_overdue_amount()
        billed_organizations = await self._invoice_repo.count_billed_organizations(
            year, month
        )
        breakdown = await self._invoice_repo.get_status_breakdown(year, month)

        total_amount = sum((amount for _, _, amount in breakdown), Decimal("0"))
        paid_amount = sum(
            (amount for status, _, amount in breakdown if status == InvoiceStatus.PAID),
            Decimal("0"),
        )
        collection_rate = (
            round(float(paid_amount / total_amount * 100), 1) if total_amount else 0.0
        )

        return BillingSummaryResponse(
            current_month_revenue=revenue,
            overdue_amount=overdue,
            billed_organizations_count=billed_organizations,
            collection_rate=collection_rate,
        )

    async def get_invoice_status_breakdown(self) -> InvoiceStatusBreakdownResponse:
        year, month = current_period()
        rows = await self._invoice_repo.get_status_breakdown(year, month)
        return InvoiceStatusBreakdownResponse(
            items=[
                InvoiceStatusBreakdownItem(
                    status=status, count=count, total_amount=amount
                )
                for status, count, amount in rows
            ]
        )

    async def get_revenue_by_channel(self) -> RevenueByChannelResponse:
        since_year, since_month = last_n_months(_REVENUE_WINDOW)[0]
        rows = await self._invoice_repo.get_revenue_by_channel(since_year, since_month)
        return RevenueByChannelResponse(
            items=[
                RevenueByChannelItem(channel_name=channel_name, total_amount=amount)
                for channel_name, amount in rows
            ]
        )

    async def get_revenue_by_provider(self) -> RevenueByProviderResponse:
        since_year, since_month = last_n_months(_REVENUE_WINDOW)[0]
        rows = await self._invoice_repo.get_revenue_by_provider(since_year, since_month)
        return RevenueByProviderResponse(
            items=[
                RevenueByProviderItem(provider=provider, total_amount=amount)
                for provider, amount in rows
            ]
        )

    async def get_monthly_revenue(self) -> MonthlyRevenueResponse:
        months = last_n_months(_REVENUE_WINDOW)
        since_year, since_month = months[0]
        rows = await self._invoice_repo.get_monthly_revenue(since_year, since_month)
        amounts_by_month = {(year, month): amount for year, month, amount in rows}

        points = [
            MonthlyRevenuePoint(
                period=f"{year}-{month:02d}",
                total_amount=amounts_by_month.get((year, month), Decimal("0")),
            )
            for year, month in months
        ]
        return MonthlyRevenueResponse(points=points)
