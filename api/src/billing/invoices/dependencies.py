from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from billing.gateways.resolver import PaymentGatewayResolver
from billing.invoices.repository.invoice_repository import InvoiceRepository
from billing.invoices.repository.payment_attempt_repository import InvoicePaymentAttemptRepository
from billing.invoices.services.invoice_service import InvoiceService
from identity.organizations.repository.organization_repository import OrganizationRepository
from messaging.contacts.repository.contact_repository import ContactRepository


def get_invoice_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> InvoiceService:
    return InvoiceService(
        session,
        InvoiceRepository(session),
        InvoicePaymentAttemptRepository(session),
        ContactRepository(session),
        OrganizationRepository(session),
        PaymentGatewayResolver(),
    )


InvoiceServiceDep = Annotated[InvoiceService, Depends(get_invoice_service)]
