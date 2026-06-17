from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from billing.invoices.repository.invoice_repository import InvoiceRepository
from billing.invoices.repository.payment_attempt_repository import PaymentAttemptRepository
from billing.invoices.services.invoice_service import InvoiceService
from messaging.contacts.repositories.contact_repository import ContactRepository


def get_invoice_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> InvoiceService:
    return InvoiceService(
        session, InvoiceRepository(session), PaymentAttemptRepository(session), ContactRepository(session)
    )


InvoiceServiceDep = Annotated[InvoiceService, Depends(get_invoice_service)]
