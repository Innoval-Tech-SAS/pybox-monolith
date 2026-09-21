import uuid
from typing import Sequence

from sqlalchemy import select

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.ivr.models.ivr_execution_model import IvrExecutionModel


class IvrExecutionRepository(SoftDeleteRepositoryBase[IvrExecutionModel]):
    model_class = IvrExecutionModel

    async def get_by_bulk_id(self, bulk_id: str) -> IvrExecutionModel | None:
        result = await self.session.execute(
            select(IvrExecutionModel).where(IvrExecutionModel.bulk_id == bulk_id)
        )
        return result.scalar_one_or_none()

    async def list_by_campaign(self, campaign_id: uuid.UUID) -> Sequence[IvrExecutionModel]:
        result = await self.session.execute(
            select(IvrExecutionModel)
            .where(IvrExecutionModel.campaign_id == campaign_id)
            .order_by(IvrExecutionModel.dispatched_at.desc())
        )
        return result.scalars().all()

    async def get_latest_for_campaign(self, campaign_id: uuid.UUID) -> IvrExecutionModel | None:
        """El bulk más reciente de la campaña (activo o no).

        Con envíos grandes troceados en varios bulks (`BATCH_SIZE`), "el más
        reciente" no siempre es "el único en curso" — el monitor y los
        controles dejan claro sobre cuál se está actuando.
        """
        result = await self.session.execute(
            select(IvrExecutionModel)
            .where(IvrExecutionModel.campaign_id == campaign_id)
            .order_by(IvrExecutionModel.dispatched_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
