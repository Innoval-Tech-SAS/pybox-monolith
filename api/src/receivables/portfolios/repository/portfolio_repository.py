import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.portfolios.models.portfolio_model import PortfolioModel
from receivables.portfolios.models.portfolio_user_access_model import PortfolioUserAccessModel


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

    async def count_active_inactive_by_organization_id(self, organization_id: uuid.UUID) -> tuple[int, int]:
        """Retorna (activos, inactivos) en una sola query agregada."""
        result = await self.session.execute(
            select(PortfolioModel.is_active, func.count(PortfolioModel.id))
            .where(
                PortfolioModel.organization_id == organization_id,
                PortfolioModel.deleted_at.is_(None),
            )
            .group_by(PortfolioModel.is_active)
        )
        counts = dict(result.all())
        return counts.get(True, 0), counts.get(False, 0)

    async def get_active_accessible_by_user_and_org(
        self, user_id: uuid.UUID, organization_id: uuid.UUID
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
        user_id: uuid.UUID,
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

    async def soft_delete_by_organization(self, organization_id: uuid.UUID, deleted_at: datetime) -> list[uuid.UUID]:
        """Baja en cascada de los portafolios vivos de la organización con el sello de la
        organización. Devuelve los ids afectados para que el service propague la cascada
        a lo que cuelga de ellos (créditos, campañas)."""
        result = await self.session.execute(
            select(PortfolioModel.id).where(
                PortfolioModel.organization_id == organization_id,
                PortfolioModel.deleted_at.is_(None),
            )
        )
        portfolio_ids = list(result.scalars().all())
        await self.soft_delete_where(PortfolioModel.id.in_(portfolio_ids), deleted_at=deleted_at)
        return portfolio_ids

    async def restore_by_organization(self, organization_id: uuid.UUID, deleted_at: datetime) -> list[uuid.UUID]:
        """Inverso de ``soft_delete_by_organization``: solo los portafolios que cayeron con
        esa organización (mismo sello), no los que ya estaban eliminados antes."""
        result = await self.session.execute(
            select(PortfolioModel.id).where(
                PortfolioModel.organization_id == organization_id,
                PortfolioModel.deleted_at == deleted_at,
            )
        )
        portfolio_ids = list(result.scalars().all())
        await self.restore_where(PortfolioModel.id.in_(portfolio_ids), deleted_at=deleted_at)
        return portfolio_ids
