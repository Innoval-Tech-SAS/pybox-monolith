import uuid
from typing import Sequence

from sqlalchemy import select

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.segments.models.segment_execution_model import SegmentExecutionModel


class SegmentExecutionRepository(SoftDeleteRepositoryBase[SegmentExecutionModel]):
    model_class = SegmentExecutionModel

    async def get_by_segment(
        self, segment_id: uuid.UUID
    ) -> Sequence[SegmentExecutionModel]:
        result = await self.session.execute(
            select(SegmentExecutionModel)
            .where(SegmentExecutionModel.segment_id == segment_id)
            .order_by(SegmentExecutionModel.created_at.desc())
        )
        return result.scalars().all()
