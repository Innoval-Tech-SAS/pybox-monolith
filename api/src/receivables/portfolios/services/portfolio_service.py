import uuid
from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from pydantic import TypeAdapter

from app_platform.dashboard.schemas.dashboard_schemas import MonthlySendsPoint, MonthlySendsResponse, SendStatusCountItem, SendStatusCountsResponse
from app_platform.dashboard.utils.dashboard_utils import last_n_months
from core.cache.cache_service import cache_service
from messaging.campaigns.repository.campaign_repository import CampaignRepository
from messaging.contacts.repository.contact_repository import ContactRepository
from receivables.credits.repository.credit_repository import CreditRepository
from receivables.portfolios.models.portfolio_daily_counter_config_model import PortfolioDailyCounterConfigModel
from receivables.portfolios.models.portfolio_model import PortfolioModel
from receivables.portfolios.repository.portfolio_daily_counter_config_repository import PortfolioDailyCounterConfigRepository
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository
from receivables.portfolios.repository.portfolio_user_access_repository import PortfolioUserAccessRepository
from receivables.portfolios.schemas.portfolio_schemas import (
    PortfolioDailyCounterConfigSyncRequest,
    PortfolioDailyCounterConfigUpdateRequest,
    PortfolioStatsResponse,
    PortfolioUpdateRequest,
)
from identity.users.enums.user_enums import UserRole
from identity.users.schemas.user_session_schema import UserSession

_MONTHLY_SENDS_WINDOW = 12

_stats_adapter: TypeAdapter[PortfolioStatsResponse] = TypeAdapter(PortfolioStatsResponse)
_send_status_adapter: TypeAdapter[SendStatusCountsResponse] = TypeAdapter(SendStatusCountsResponse)
_monthly_sends_adapter: TypeAdapter[MonthlySendsResponse] = TypeAdapter(MonthlySendsResponse)


class PortfolioService:
    def __init__(
        self,
        portfolio_repo: PortfolioRepository,
        daily_counter_repo: PortfolioDailyCounterConfigRepository,
        credit_repo: CreditRepository,
        campaign_repo: CampaignRepository,
        contact_repo: ContactRepository,
        access_repo: PortfolioUserAccessRepository,
    ) -> None:
        self.portfolio_repo = portfolio_repo
        self.daily_counter_repo = daily_counter_repo
        self._credit_repo = credit_repo
        self._campaign_repo = campaign_repo
        self._contact_repo = contact_repo
        self._access_repo = access_repo

    async def list_accessible_portfolios(
        self,
        session: UserSession,
        organization_id: uuid.UUID | None = None,
        is_active: bool | None = None,
    ) -> list[PortfolioModel]:
        if session.is_global:
            if organization_id is not None:
                return await self.portfolio_repo.list_by_organization_id(
                    organization_id,
                    is_active=is_active,
                )
            return await self.portfolio_repo.list_all(is_active=is_active)

        org_entry = session.orgs[str(organization_id)]
        if org_entry.role == UserRole.ADMIN:
            return await self.portfolio_repo.list_by_organization_id(
                organization_id,
                is_active=is_active,
            )

        return await self.portfolio_repo.list_accessible_by_user_and_org(
            session.user_id,
            organization_id,
            is_active=is_active,
        )

    async def get_stats(self, portfolio_id: uuid.UUID) -> PortfolioStatsResponse:
        async def _fetch() -> PortfolioStatsResponse:
            stats = await self._credit_repo.get_portfolio_stats(portfolio_id)
            usuarios_con_acceso = await self._access_repo.count_active_users_for_portfolio(portfolio_id)
            return PortfolioStatsResponse(
                creditos=stats.creditos,
                titulares=stats.titulares,
                codeudores=stats.codeudores,
                clientes_unicos=stats.clientes_unicos,
                total_mora=stats.total_mora,
                documentos_unicos=stats.documentos_unicos,
                creditos_cargados=stats.creditos,
                usuarios_con_acceso=usuarios_con_acceso,
            )
        return await cache_service.get_or_set(
            key=f"portfolio:stats:{portfolio_id}",
            fetch=_fetch,
            adapter=_stats_adapter,
            ttl=120,
        )

    async def get_monthly_sends(self, portfolio_id: uuid.UUID, campaign_id: uuid.UUID) -> MonthlySendsResponse:
        async def _fetch() -> MonthlySendsResponse:
            portfolio = await self.get_by_id(portfolio_id)
            campaign = await self._campaign_repo.get_by_id_and_portfolio(campaign_id, portfolio_id)
            if campaign is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Campaña no encontrada en este portafolio")
            months = last_n_months(_MONTHLY_SENDS_WINDOW)
            period_start = datetime(months[0][0], months[0][1], 1, tzinfo=timezone.utc)
            rows = await self._contact_repo.get_monthly_sends_by_campaign(
                portfolio.organization_id, campaign_id, period_start
            )
            counts_by_month = {(d.year, d.month): count for d, count in rows}
            points = [
                MonthlySendsPoint(period=f"{year}-{month:02d}", count=counts_by_month.get((year, month), 0))
                for year, month in months
            ]
            return MonthlySendsResponse(campaign_id=campaign.id, campaign_name=campaign.name, points=points)
        return await cache_service.get_or_set(
            key=f"portfolio:monthly-sends:{portfolio_id}:{campaign_id}",
            fetch=_fetch,
            adapter=_monthly_sends_adapter,
            ttl=300,
        )

    async def get_send_status_counts(self, portfolio_id: uuid.UUID) -> SendStatusCountsResponse:
        async def _fetch() -> SendStatusCountsResponse:
            portfolio = await self.get_by_id(portfolio_id)
            rows = await self._contact_repo.get_send_status_counts(portfolio.organization_id, portfolio_id)
            return SendStatusCountsResponse(
                items=[SendStatusCountItem(status=s, count=c) for s, c in rows]
            )
        return await cache_service.get_or_set(
            key=f"portfolio:send-status:{portfolio_id}",
            fetch=_fetch,
            adapter=_send_status_adapter,
            ttl=120,
        )

    async def get_by_id(self, portfolio_id: uuid.UUID) -> PortfolioModel:
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if portfolio is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portafolio no encontrado")
        return portfolio

    async def update_portfolio(
        self, portfolio_id: uuid.UUID, data: PortfolioUpdateRequest
    ) -> PortfolioModel:
        portfolio = await self.get_by_id(portfolio_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(portfolio, key, value)
        return await self.portfolio_repo.update(portfolio)

    async def delete_portfolio(self, portfolio_id: uuid.UUID) -> None:
        portfolio = await self.get_by_id(portfolio_id)
        await self.portfolio_repo.delete(portfolio)

    async def restore_portfolio(self, portfolio_id: uuid.UUID) -> PortfolioModel:
        portfolio = await self.portfolio_repo.get_by_id_including_deleted(portfolio_id)
        if portfolio is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portafolio no encontrado")
        return await self.portfolio_repo.restore(portfolio)

    async def get_daily_counter_config(
        self, portfolio_id: uuid.UUID
    ) -> PortfolioDailyCounterConfigModel | None:
        return await self.daily_counter_repo.get_by_portfolio_id(portfolio_id)

    async def update_daily_counter_config(
        self,
        portfolio_id: uuid.UUID,
        data: PortfolioDailyCounterConfigUpdateRequest,
        updated_by: uuid.UUID,
    ) -> PortfolioDailyCounterConfigModel:
        config = await self.daily_counter_repo.get_by_portfolio_id(portfolio_id)
        if config is None:
            config = PortfolioDailyCounterConfigModel(
                portfolio_id=portfolio_id,
                enabled=data.enabled if data.enabled is not None else False,
                reactivation_mode=data.reactivation_mode or "FROM_TODAY",
                updated_by=updated_by,
            )
            return await self.daily_counter_repo.add(config)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(config, key, value)
        config.updated_by = updated_by
        return await self.daily_counter_repo.update(config)

    async def sync_daily_counter_config(
        self,
        portfolio_id: uuid.UUID,
        data: PortfolioDailyCounterConfigSyncRequest,
        updated_by: uuid.UUID,
    ) -> PortfolioDailyCounterConfigModel:
        config = await self.daily_counter_repo.get_by_portfolio_id(portfolio_id)
        if config is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe configuración de contador diario para este portafolio",
            )
        config.last_synced_at = datetime.now(timezone.utc)
        config.last_synced_cutoff_date = data.target_date or date.today()
        config.updated_by = updated_by
        return await self.daily_counter_repo.update(config)

