"""Dependencia de FastAPI para inyectar el CampaignService con sus repositories."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.schema_manager.services.dml_service import DmlService
from app_platform.support.services.support_service import SupportService
from billing.billing_status.services.billing_status_service import BillingStatusService
from billing.invoices.repository.invoice_repository import InvoiceRepository
from core.database.database import get_main_session
from messaging.campaigns.repository.campaign_repository import CampaignRepository
from messaging.campaigns.repository.campaign_time_repository import (
    CampaignTimeRepository,
)
from messaging.campaigns.services.campaign_service import CampaignService
from messaging.campaigns.services.recipient_count_service import RecipientCountService
from messaging.channels.repository.channel_repository import ChannelRepository
from messaging.ivr.repository.ivr_flow_repository import IvrFlowRepository
from messaging.templates.repository.template_repository import TemplateRepository
from messaging.whatsapp.repository.whatsapp_org_credentials_repository import (
    WhatsAppOrgCredentialsRepository,
)
from messaging.whatsapp.services.whatsapp_number_request_service import (
    WhatsAppNumberRequestService,
)
from receivables.contact_methods.repository.contact_method_repository import (
    ContactMethodRepository,
)
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository
from receivables.segments.repository.segment_repository import SegmentRepository


def get_campaign_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> CampaignService:
    segment_repo = SegmentRepository(session)
    channel_repo = ChannelRepository(session)
    return CampaignService(
        CampaignRepository(session),
        CampaignTimeRepository(session),
        BillingStatusService(InvoiceRepository(session)),
        PortfolioRepository(session),
        TemplateRepository(session),
        channel_repo,
        segment_repo,
        RecipientCountService(
            segment_repo,
            channel_repo,
            ContactMethodRepository(session),
            DmlService(session),
            PortfolioRepository(session),
        ),
        WhatsAppNumberRequestService(
            WhatsAppOrgCredentialsRepository(session), SupportService(session)
        ),
        IvrFlowRepository(session),
    )


CampaignServiceDep = Annotated[CampaignService, Depends(get_campaign_service)]
