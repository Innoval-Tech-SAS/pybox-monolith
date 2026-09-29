from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from billing.billing_status.services.billing_status_service import BillingStatusService
from billing.invoices.repository.invoice_repository import InvoiceRepository
from core.database.database import get_main_session


def get_billing_status_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> BillingStatusService:
    return BillingStatusService(InvoiceRepository(session))


BillingStatusServiceDep = Annotated[
    BillingStatusService, Depends(get_billing_status_service)
]
