import uuid
from datetime import datetime

from sqlalchemy import func, select

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.portfolios.models.portfolio_user_access_model import (
    PortfolioUserAccessModel,
)


class PortfolioUserAccessRepository(SoftDeleteRepositoryBase[PortfolioUserAccessModel]):
    model_class = PortfolioUserAccessModel

    async def get_by_user_and_org(
        self, user_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[PortfolioUserAccessModel]:
        result = await self.session.execute(
            select(PortfolioUserAccessModel).where(
                PortfolioUserAccessModel.user_id == user_id,
                PortfolioUserAccessModel.organization_id == organization_id,
                PortfolioUserAccessModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_active_by_user_and_org(
        self, user_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[PortfolioUserAccessModel]:
        result = await self.session.execute(
            select(PortfolioUserAccessModel).where(
                PortfolioUserAccessModel.user_id == user_id,
                PortfolioUserAccessModel.organization_id == organization_id,
                PortfolioUserAccessModel.is_active.is_(True),
                PortfolioUserAccessModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_by_portfolio_id(
        self, portfolio_id: uuid.UUID
    ) -> list[PortfolioUserAccessModel]:
        result = await self.session.execute(
            select(PortfolioUserAccessModel).where(
                PortfolioUserAccessModel.portfolio_id == portfolio_id,
                PortfolioUserAccessModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_by_user_and_portfolio(
        self,
        user_id: uuid.UUID,
        portfolio_id: uuid.UUID,
        organization_id: uuid.UUID | None = None,
    ) -> PortfolioUserAccessModel | None:
        conditions = [
            PortfolioUserAccessModel.user_id == user_id,
            PortfolioUserAccessModel.portfolio_id == portfolio_id,
            PortfolioUserAccessModel.deleted_at.is_(None),
        ]
        if organization_id is not None:
            conditions.append(
                PortfolioUserAccessModel.organization_id == organization_id
            )

        result = await self.session.execute(
            select(PortfolioUserAccessModel).where(*conditions)
        )
        return result.scalars().first()

    async def get_distinct_org_ids_by_user(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        result = await self.session.execute(
            select(PortfolioUserAccessModel.organization_id)
            .where(
                PortfolioUserAccessModel.user_id == user_id,
                PortfolioUserAccessModel.is_active.is_(True),
                PortfolioUserAccessModel.deleted_at.is_(None),
            )
            .distinct()
        )
        return list(result.scalars().all())

    async def get_active_user_ids_for_portfolio(
        self, portfolio_id: uuid.UUID
    ) -> list[uuid.UUID]:
        result = await self.session.execute(
            select(PortfolioUserAccessModel.user_id).where(
                PortfolioUserAccessModel.portfolio_id == portfolio_id,
                PortfolioUserAccessModel.is_active.is_(True),
                PortfolioUserAccessModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def count_active_users_for_portfolio(self, portfolio_id: uuid.UUID) -> int:
        return (
            await self.session.scalar(
                select(func.count())
                .select_from(PortfolioUserAccessModel)
                .where(
                    PortfolioUserAccessModel.portfolio_id == portfolio_id,
                    PortfolioUserAccessModel.is_active.is_(True),
                    PortfolioUserAccessModel.deleted_at.is_(None),
                )
            )
            or 0
        )

    async def check_active_access(
        self,
        user_id: uuid.UUID,
        portfolio_id: uuid.UUID,
        organization_id: uuid.UUID | None = None,
    ) -> bool:
        record = await self.get_by_user_and_portfolio(
            user_id, portfolio_id, organization_id
        )
        return record is not None and record.is_active

    async def soft_delete_by_organization(
        self, organization_id: uuid.UUID, deleted_at: datetime
    ) -> None:
        """Baja en cascada de los accesos de usuarios a portafolios de la
        organización con el sello de la organización."""
        await self.soft_delete_where(
            PortfolioUserAccessModel.organization_id == organization_id,
            deleted_at=deleted_at,
        )

    async def restore_by_organization(
        self, organization_id: uuid.UUID, deleted_at: datetime
    ) -> None:
        """Inverso de ``soft_delete_by_organization``: solo lo que cayó con la
        organización."""
        await self.restore_where(
            PortfolioUserAccessModel.organization_id == organization_id,
            deleted_at=deleted_at,
        )
