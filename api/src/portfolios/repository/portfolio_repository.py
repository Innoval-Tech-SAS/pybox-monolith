import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.soft_delete_repository_base import SoftDeleteRepositoryBase
from portfolios.models.portfolio_model import PortfolioModel
from portfolios.models.portfolio_user_access_model import PortfolioUserAccessModel


class PortfolioRepository(SoftDeleteRepositoryBase[PortfolioModel]):
    model_class = PortfolioModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_ids(self, ids: list[uuid.UUID]) -> list[PortfolioModel]:
        if not ids:
            return []
        result = await self.session.execute(
            select(PortfolioModel).where(
                PortfolioModel.id.in_(ids),
                PortfolioModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_by_organization_id(self, organization_id: uuid.UUID) -> list[PortfolioModel]:
        return await self.list_by_organization_id(organization_id)

    async def get_active_by_organization_id(self, organization_id: uuid.UUID) -> list[PortfolioModel]:
        return await self.list_by_organization_id(organization_id, is_active=True)

    async def get_active_all(self) -> list[PortfolioModel]:
        return await self.list_all(is_active=True)

    async def get_active_accessible_by_user_and_org(
        self, user_id: int, organization_id: uuid.UUID
    ) -> list[PortfolioModel]:
        return await self.list_accessible_by_user_and_org(
            user_id,
            organization_id,
            is_active=True,
        )

    async def list_all(self, is_active: bool | None = None) -> list[PortfolioModel]:
        conditions = [PortfolioModel.deleted_at.is_(None)]
        if is_active is not None:
            conditions.append(PortfolioModel.is_active.is_(is_active))

        result = await self.session.execute(
            select(PortfolioModel).where(*conditions).order_by(PortfolioModel.id.asc())
        )
        return list(result.scalars().all())

    async def list_by_organization_id(
        self, organization_id: uuid.UUID, is_active: bool | None = None
    ) -> list[PortfolioModel]:
        conditions = [
            PortfolioModel.organization_id == organization_id,
            PortfolioModel.deleted_at.is_(None),
        ]
        if is_active is not None:
            conditions.append(PortfolioModel.is_active.is_(is_active))

        result = await self.session.execute(
            select(PortfolioModel).where(*conditions).order_by(PortfolioModel.id.asc())
        )
        return list(result.scalars().all())

    async def list_accessible_by_user_and_org(
        self,
        user_id: int,
        organization_id: uuid.UUID,
        is_active: bool | None = None,
    ) -> list[PortfolioModel]:
        conditions = [
            PortfolioModel.organization_id == organization_id,
            PortfolioModel.deleted_at.is_(None),
            PortfolioUserAccessModel.user_id == user_id,
            PortfolioUserAccessModel.organization_id == organization_id,
            PortfolioUserAccessModel.is_active.is_(True),
            PortfolioUserAccessModel.deleted_at.is_(None),
        ]
        if is_active is not None:
            conditions.append(PortfolioModel.is_active.is_(is_active))

        result = await self.session.execute(
            select(PortfolioModel)
            .join(
                PortfolioUserAccessModel,
                PortfolioUserAccessModel.portfolio_id == PortfolioModel.id,
            )
            .where(*conditions)
            .order_by(PortfolioModel.id.asc())
        )
        return list(result.scalars().unique().all())
