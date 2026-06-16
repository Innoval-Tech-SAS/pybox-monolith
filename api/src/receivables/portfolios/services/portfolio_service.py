import uuid
from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select, union
from sqlalchemy.ext.asyncio import AsyncSession

from receivables.credits.models.credit_model import CreditModel
from receivables.portfolios.models.portfolio_daily_counter_config_model import PortfolioDailyCounterConfigModel
from receivables.portfolios.models.portfolio_model import PortfolioModel
from receivables.portfolios.repository.portfolio_daily_counter_config_repository import PortfolioDailyCounterConfigRepository
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository
from receivables.portfolios.schemas.portfolio_schemas import (
    PortfolioDailyCounterConfigSyncRequest,
    PortfolioDailyCounterConfigUpdateRequest,
    PortfolioStatsResponse,
    PortfolioUpdateRequest,
)
from core.security.permissions import ORG_PORTFOLIOS
from identity.users.enums.user_enums import UserRole
from identity.users.schemas.user_session_schema import UserSession


class PortfolioService:
    def __init__(
        self,
        session: AsyncSession,
        portfolio_repo: PortfolioRepository,
        daily_counter_repo: PortfolioDailyCounterConfigRepository,
    ) -> None:
        self._session = session
        self.portfolio_repo = portfolio_repo
        self.daily_counter_repo = daily_counter_repo

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

        selected_org_id = organization_id or self._first_session_org_id(session)
        org_entry = session.orgs.get(str(selected_org_id))
        if org_entry is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sin acceso a esta organización",
            )

        if ORG_PORTFOLIOS not in org_entry.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para consultar portfolios",
            )

        if org_entry.role == UserRole.ADMIN:
            return await self.portfolio_repo.list_by_organization_id(
                selected_org_id,
                is_active=is_active,
            )

        return await self.portfolio_repo.list_accessible_by_user_and_org(
            session.user_id,
            selected_org_id,
            is_active=is_active,
        )

    async def get_stats(self, portfolio_id: uuid.UUID) -> PortfolioStatsResponse:
        result = await self._session.execute(
            select(
                func.count(CreditModel.id).label("creditos"),
                func.count(func.distinct(CreditModel.debtor_id)).label("titulares"),
                func.count(func.distinct(CreditModel.codebtor_id)).label("codeudores"),
            ).where(CreditModel.portfolio_id == portfolio_id)
        )
        row = result.one()

        debtors_q = select(CreditModel.debtor_id.label("id")).where(
            CreditModel.portfolio_id == portfolio_id
        )
        codebtors_q = select(CreditModel.codebtor_id.label("id")).where(
            CreditModel.portfolio_id == portfolio_id,
            CreditModel.codebtor_id.is_not(None),
        )
        all_ids = union(debtors_q, codebtors_q).subquery()
        clientes_unicos: int = await self._session.scalar(
            select(func.count()).select_from(all_ids)
        ) or 0

        return PortfolioStatsResponse(
            creditos=row.creditos,
            titulares=row.titulares,
            codeudores=row.codeudores,
            clientes_unicos=clientes_unicos,
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

    async def get_daily_counter_config(
        self, portfolio_id: uuid.UUID
    ) -> PortfolioDailyCounterConfigModel | None:
        return await self.daily_counter_repo.get_by_portfolio_id(portfolio_id)

    async def update_daily_counter_config(
        self,
        portfolio_id: uuid.UUID,
        data: PortfolioDailyCounterConfigUpdateRequest,
        updated_by: int,
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
        updated_by: int,
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

    def _first_session_org_id(self, session: UserSession) -> uuid.UUID:
        if not session.orgs:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario no pertenece a ninguna organización",
            )
        return uuid.UUID(next(iter(session.orgs)))
