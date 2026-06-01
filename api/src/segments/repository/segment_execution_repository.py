from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.repository_base import RepositoryBase
from segments.models.segment_execution_model import SegmentExecutionModel


class SegmentExecutionRepository(RepositoryBase[SegmentExecutionModel]):
    model_class = SegmentExecutionModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_segment(self, segment_id: int) -> Sequence[SegmentExecutionModel]:
        result = await self.session.execute(
            select(SegmentExecutionModel)
            .where(SegmentExecutionModel.segment_id == segment_id)
            .order_by(SegmentExecutionModel.created_at.desc())
        )
        return result.scalars().all()
