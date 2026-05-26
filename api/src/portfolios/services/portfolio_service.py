import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select, union
from sqlalchemy.ext.asyncio import AsyncSession

from credits.models.credit_model import CreditModel
from portfolios.models.portfolio_model import PortfolioModel
from portfolios.repository.portfolio_repository import PortfolioRepository
from portfolios.schemas.portfolio_schemas import PortfolioStatsResponse
from security.permissions import ORG_PORTFOLIOS
from users.enums.user_enums import UserRole
from users.schemas.user_session_schema import UserSession


class PortfolioService:
    def __init__(self, session: AsyncSession, portfolio_repo: PortfolioRepository) -> None:
        self._session = session
        self.portfolio_repo = portfolio_repo

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

    def _first_session_org_id(self, session: UserSession) -> uuid.UUID:
        if not session.orgs:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario no pertenece a ninguna organización",
            )
        return uuid.UUID(next(iter(session.orgs)))
