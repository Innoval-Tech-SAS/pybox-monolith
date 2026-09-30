"""Endpoints del dashboard de facturación para administradores globales."""

from billing.billing_dashboard.dependencies import BillingDashboardServiceDep
from billing.billing_dashboard.schemas.billing_dashboard_schemas import (
    BillingSummaryResponse,
    InvoiceStatusBreakdownResponse,
    MonthlyRevenueResponse,
    RevenueByChannelResponse,
    RevenueByProviderResponse,
)
from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_global_admin

router = APIRouter(prefix="/billing/admin/dashboard", tags=["Facturación"])


@router.get(
    "/summary",
    response_model=BillingSummaryResponse,
    summary="Resumen de facturación global del periodo actual (solo admin global)",
)
async def get_billing_summary(
    session: CurrentSession,
    service: BillingDashboardServiceDep,
) -> BillingSummaryResponse:
    require_global_admin(session)
    return await service.get_summary()


@router.get(
    "/invoices-by-status",
    response_model=InvoiceStatusBreakdownResponse,
    summary="Facturas del periodo actual agrupadas por estado (solo admin global)",
)
async def get_invoices_by_status(
    session: CurrentSession,
    service: BillingDashboardServiceDep,
) -> InvoiceStatusBreakdownResponse:
    require_global_admin(session)
    return await service.get_invoice_status_breakdown()


@router.get(
    "/revenue-by-channel",
    response_model=RevenueByChannelResponse,
    summary="Ingreso por canal en los últimos 12 meses (solo admin global)",
)
async def get_revenue_by_channel(
    session: CurrentSession,
    service: BillingDashboardServiceDep,
) -> RevenueByChannelResponse:
    require_global_admin(session)
    return await service.get_revenue_by_channel()


@router.get(
    "/revenue-by-provider",
    response_model=RevenueByProviderResponse,
    summary=(
        "Ingreso cobrado por pasarela de pago en los últimos 12 meses "
        "(solo admin global)"
    ),
)
async def get_revenue_by_provider(
    session: CurrentSession,
    service: BillingDashboardServiceDep,
) -> RevenueByProviderResponse:
    require_global_admin(session)
    return await service.get_revenue_by_provider()


@router.get(
    "/monthly-revenue",
    response_model=MonthlyRevenueResponse,
    summary="Facturación mensual global de los últimos 12 meses (solo admin global)",
)
async def get_monthly_revenue(
    session: CurrentSession,
    service: BillingDashboardServiceDep,
) -> MonthlyRevenueResponse:
    require_global_admin(session)
    return await service.get_monthly_revenue()
