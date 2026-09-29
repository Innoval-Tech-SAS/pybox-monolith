from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from billing.billing_dashboard.services.billing_dashboard_service import (
    BillingDashboardService,
)
from billing.invoices.repository.invoice_repository import InvoiceRepository
from core.database.database import get_main_session


def get_billing_dashboard_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> BillingDashboardService:
    return BillingDashboardService(InvoiceRepository(session))


BillingDashboardServiceDep = Annotated[
    BillingDashboardService, Depends(get_billing_dashboard_service)
]
