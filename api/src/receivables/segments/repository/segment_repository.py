import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.segments.models.segment_model import SegmentModel


class SegmentRepository(SoftDeleteRepositoryBase[SegmentModel]):
    model_class = SegmentModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_organization(self, organization_id: uuid.UUID) -> Sequence[SegmentModel]:
        result = await self.session.execute(
            select(SegmentModel).where(
                SegmentModel.organization_id == organization_id,
                SegmentModel.deleted_at.is_(None),
            )
        )
        return result.scalars().all()
