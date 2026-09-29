from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.support.services.support_service import SupportService
from billing.billing_status.services.billing_status_service import BillingStatusService
from billing.invoices.repository.invoice_repository import InvoiceRepository
from core.database.database import get_main_session
from messaging.bulk_send.services.bulk_send_service import BulkSendService
from messaging.campaigns.repository.campaign_repository import CampaignRepository
from messaging.campaigns.services.batch_sender import BatchSender
from messaging.channels.repository.channel_repository import ChannelRepository
from messaging.contacts.repository.contact_repository import ContactRepository
from messaging.dispatcher import MessageDispatcher
from messaging.templates.repository.template_repository import TemplateRepository
from messaging.whatsapp.repository.whatsapp_channel_request_repository import (
    WhatsAppChannelRequestRepository,
)
from messaging.whatsapp.repository.whatsapp_org_credentials_repository import (
    WhatsAppOrgCredentialsRepository,
)
from messaging.whatsapp.repository.whatsapp_template_data_repository import (
    WhatsAppTemplateDataRepository,
)
from messaging.whatsapp.services.whatsapp_channel_request_service import (
    WhatsAppChannelRequestService,
)
from messaging.whatsapp.services.whatsapp_number_request_service import (
    WhatsAppNumberRequestService,
)
from receivables.debtors.repository.debtor_repository import DebtorRepository
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository

_DISPATCHER = MessageDispatcher()


def get_bulk_send_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> BulkSendService:
    return BulkSendService(
        debtor_repo=DebtorRepository(session),
        channel_repo=ChannelRepository(session),
        template_repo=TemplateRepository(session),
        portfolio_repo=PortfolioRepository(session),
        campaign_repo=CampaignRepository(session),
        batch_sender=BatchSender(_DISPATCHER, ContactRepository(session)),
        billing_status_service=BillingStatusService(InvoiceRepository(session)),
        whatsapp_credentials_repo=WhatsAppOrgCredentialsRepository(session),
        whatsapp_template_data_repo=WhatsAppTemplateDataRepository(session),
        whatsapp_channel_request_service=WhatsAppChannelRequestService(
            WhatsAppChannelRequestRepository(session)
        ),
        whatsapp_number_request_service=WhatsAppNumberRequestService(
            WhatsAppOrgCredentialsRepository(session), SupportService(session)
        ),
    )


BulkSendServiceDep = Annotated[BulkSendService, Depends(get_bulk_send_service)]
