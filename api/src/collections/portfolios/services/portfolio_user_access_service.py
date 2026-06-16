import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from collections.portfolios.models.portfolio_user_access_model import PortfolioUserAccessModel
from collections.portfolios.repository.portfolio_repository import PortfolioRepository
from collections.portfolios.repository.portfolio_user_access_repository import PortfolioUserAccessRepository


class PortfolioUserAccessService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = PortfolioUserAccessRepository(session)
        self._portfolio_repo = PortfolioRepository(session)

    async def check_access(self, user_id: int, portfolio_id: uuid.UUID, org_id: str) -> bool:
        try:
            organization_id = uuid.UUID(str(org_id))
            portfolio_uuid = uuid.UUID(str(portfolio_id))
        except ValueError:
            return False
        return await self._repo.check_active_access(user_id, portfolio_uuid, organization_id)

    async def grant_access(
        self,
        user_id: int,
        portfolio_id: uuid.UUID,
        organization_id: uuid.UUID,
        granted_by: int,
    ) -> PortfolioUserAccessModel:
        existing = await self._repo.get_by_user_and_portfolio(user_id, portfolio_id)
        if existing is not None:
            if existing.is_active:
                return existing
            existing.is_active = True
            existing.revoked_at = None
            existing.granted_by = granted_by
            existing.granted_at = datetime.utcnow()
            return await self._repo.update(existing)

        return await self._repo.add(PortfolioUserAccessModel(
            user_id=user_id,
            portfolio_id=portfolio_id,
            organization_id=organization_id,
            granted_by=granted_by,
        ))

    async def revoke_access(self, user_id: int, portfolio_id: uuid.UUID) -> None:
        existing = await self._repo.get_by_user_and_portfolio(user_id, portfolio_id)
        if existing is None or not existing.is_active:
            return
        existing.is_active = False
        existing.revoked_at = datetime.utcnow()
        await self._repo.update(existing)

    async def get_user_portfolios(
        self, user_id: int, organization_id: uuid.UUID
    ) -> list[PortfolioUserAccessModel]:
        return await self._repo.get_active_by_user_and_org(user_id, organization_id)

    async def revoke_all_for_user_in_org(
        self, user_id: int, organization_id: uuid.UUID
    ) -> None:
        accesses = await self._repo.get_active_by_user_and_org(user_id, organization_id)
        now = datetime.utcnow()
        for access in accesses:
            access.is_active = False
            access.revoked_at = now
            await self._repo.update(access)

    async def list_org_portfolios_with_access_status(
        self, user_id: int, organization_id: uuid.UUID
    ) -> list[tuple[uuid.UUID, str, bool]]:
        all_portfolios = await self._portfolio_repo.get_active_by_organization_id(organization_id)
        active_accesses = await self._repo.get_active_by_user_and_org(user_id, organization_id)
        granted_ids = {a.portfolio_id for a in active_accesses}
        return [(p.id, p.name, p.id in granted_ids) for p in all_portfolios]

    async def list_portfolio_access(
        self, portfolio_id: uuid.UUID
    ) -> list[PortfolioUserAccessModel]:
        return await self._repo.get_by_portfolio_id(portfolio_id)

    async def replace_access(
        self,
        portfolio_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_ids: list[int],
        granted_by: int,
    ) -> list[PortfolioUserAccessModel]:
        existing = await self._repo.get_by_portfolio_id(portfolio_id)
        existing_by_user = {a.user_id: a for a in existing}
        new_set = set(user_ids)

        for user_id, access in existing_by_user.items():
            if user_id not in new_set and access.is_active:
                await self.revoke_access(user_id, portfolio_id)

        result = []
        for user_id in user_ids:
            access = await self.grant_access(user_id, portfolio_id, organization_id, granted_by)
            result.append(access)

        return result
