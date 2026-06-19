import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.segments.models.segment_model import SegmentModel


class SegmentRepository(SoftDeleteRepositoryBase[SegmentModel]):
    model_class = SegmentModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_all_by_organization(self, organization_id: uuid.UUID) -> list[SegmentModel]:
        result = await self.session.execute(
            select(SegmentModel)
            .where(
                SegmentModel.organization_id == organization_id,
                SegmentModel.deleted_at.is_(None),
            )
            .order_by(SegmentModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_organization(
        self,
        organization_id: uuid.UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[SegmentModel], int]:
        query = select(SegmentModel).where(
            SegmentModel.organization_id == organization_id,
            SegmentModel.deleted_at.is_(None),
        )

        total: int = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        ) or 0

        result = await self.session.execute(
            query.order_by(SegmentModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total
