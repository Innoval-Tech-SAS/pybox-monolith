import uuid

from sqlalchemy import select

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.ivr.models.ivr_flow_model import IvrFlowModel


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
