import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.reports.models.report_model import ReportModel


class ReportRepository(SoftDeleteRepositoryBase[ReportModel]):
    model_class = ReportModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_organization_id(
        self,
        organization_id: uuid.UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[ReportModel], int]:
        query = select(ReportModel).where(
            ReportModel.organization_id == organization_id,
            ReportModel.deleted_at.is_(None),
        )

        total: int = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        ) or 0

        result = await self.session.execute(
            query.order_by(ReportModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_global_and_by_organization(self, organization_id: uuid.UUID) -> list[ReportModel]:
        result = await self.session.execute(
            select(ReportModel).where(
                (ReportModel.is_global.is_(True)) | (ReportModel.organization_id == organization_id),
                ReportModel.is_active.is_(True),
                ReportModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())
