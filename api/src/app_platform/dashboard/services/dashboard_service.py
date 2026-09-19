import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status

from app_platform.dashboard.schemas.dashboard_schemas import (
    DashboardCampaignOption,
    MonthlySendsPoint,
    MonthlySendsResponse,
    OrganizationStatsResponse,
    SendStatusCountItem,
    SendStatusCountsResponse,
)
from app_platform.dashboard.utils.dashboard_utils import last_n_months
from messaging.campaigns.repository.campaign_repository import CampaignRepository
from messaging.contacts.repository.contact_repository import ContactRepository
from receivables.credits.repository.credit_repository import CreditRepository
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository

_MONTHLY_SENDS_WINDOW = 12


class DashboardService:
    def __init__(
        self,
        credit_repo: CreditRepository,
        portfolio_repo: PortfolioRepository,
        campaign_repo: CampaignRepository,
        contact_repo: ContactRepository,
    ):
        self._credit_repo = credit_repo
        self._portfolio_repo = portfolio_repo
        self._campaign_repo = campaign_repo
        self._contact_repo = contact_repo

    async def get_organization_stats(self, organization_id: uuid.UUID) -> OrganizationStatsResponse:
        stats = await self._credit_repo.get_organization_stats(organization_id)
        active, inactive = await self._portfolio_repo.count_active_inactive_by_organization_id(organization_id)
        percentage = round((stats.titulares / stats.clientes_unicos) * 100, 1) if stats.clientes_unicos else 0.0

        return OrganizationStatsResponse(
            portfolios_count=active + inactive,
            portfolios_active_count=active,
            portfolios_inactive_count=inactive,
            credits_count=stats.creditos,
            debtors_count=stats.titulares,
            unique_debtors_count=stats.clientes_unicos,
            total_overdue_amount=stats.total_mora,
            debtors_loaded_percentage=percentage,
        )

    async def list_campaign_options(self, organization_id: uuid.UUID) -> list[DashboardCampaignOption]:
        campaigns = await self._campaign_repo.list_by_organization_id(organization_id)
        return [DashboardCampaignOption(id=c.id, name=c.name) for c in campaigns]

    async def get_send_status_counts(self, organization_id: uuid.UUID) -> SendStatusCountsResponse:
        rows = await self._contact_repo.get_send_status_counts(organization_id)
        return SendStatusCountsResponse(
            items=[SendStatusCountItem(status=s, count=c) for s, c in rows]
        )

    async def get_monthly_sends(
        self, organization_id: uuid.UUID, campaign_id: uuid.UUID
    ) -> MonthlySendsResponse:
        campaign = await self._campaign_repo.get_by_id_and_organization_id(campaign_id, organization_id)
        if campaign is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Campaña no encontrada")

        months = last_n_months(_MONTHLY_SENDS_WINDOW)
        period_start = datetime(months[0][0], months[0][1], 1, tzinfo=timezone.utc)

        rows = await self._contact_repo.get_monthly_sends_by_campaign(organization_id, campaign_id, period_start)
        counts_by_month = {(d.year, d.month): count for d, count in rows}

        points = [
            MonthlySendsPoint(period=f"{year}-{month:02d}", count=counts_by_month.get((year, month), 0))
            for year, month in months
        ]
        return MonthlySendsResponse(campaign_id=campaign.id, campaign_name=campaign.name, points=points)
