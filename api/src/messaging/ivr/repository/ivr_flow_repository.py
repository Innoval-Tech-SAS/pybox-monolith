"""Acceso a datos de los flujos IVR reutilizables."""

import uuid
from datetime import datetime

from sqlalchemy import select

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.ivr.models.ivr_flow_model import IvrFlowModel
from receivables.portfolios.models.portfolio_model import PortfolioModel


class IvrFlowRepository(SoftDeleteRepositoryBase[IvrFlowModel]):
    model_class = IvrFlowModel

    async def list_by_portfolio(self, portfolio_id: uuid.UUID) -> list[IvrFlowModel]:
        result = await self.session.execute(
            select(IvrFlowModel)
            .where(
                IvrFlowModel.portfolio_id == portfolio_id,
                IvrFlowModel.deleted_at.is_(None),
            )
            .order_by(IvrFlowModel.name)
        )
        return list(result.scalars().all())

    async def get_by_id_and_portfolio(
        self, flow_id: uuid.UUID, portfolio_id: uuid.UUID
    ) -> IvrFlowModel | None:
        result = await self.session.execute(
            select(IvrFlowModel).where(
                IvrFlowModel.id == flow_id,
                IvrFlowModel.portfolio_id == portfolio_id,
                IvrFlowModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def soft_delete_by_organization(
        self, organization_id: uuid.UUID, deleted_at: datetime
    ) -> None:
        """Baja en cascada de los flujos IVR de los portafolios de la
        organización con el sello de la organización."""
        await self.soft_delete_where(
            IvrFlowModel.portfolio_id.in_(
                select(PortfolioModel.id).where(
                    PortfolioModel.organization_id == organization_id
                )
            ),
            deleted_at=deleted_at,
        )

    async def restore_by_organization(
        self, organization_id: uuid.UUID, deleted_at: datetime
    ) -> None:
        """Inverso de ``soft_delete_by_organization``: solo lo que cayó
        con la organización."""
        await self.restore_where(
            IvrFlowModel.portfolio_id.in_(
                select(PortfolioModel.id).where(
                    PortfolioModel.organization_id == organization_id
                )
            ),
            deleted_at=deleted_at,
        )
