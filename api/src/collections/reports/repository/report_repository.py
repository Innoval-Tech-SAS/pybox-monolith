import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from collections.reports.models.report_model import ReportModel


class ReportRepository(SoftDeleteRepositoryBase[ReportModel]):
    model_class = ReportModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_organization_id(self, organization_id: uuid.UUID) -> list[ReportModel]:
        result = await self.session.execute(
            select(ReportModel).where(
                ReportModel.organization_id == organization_id,
                ReportModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_global_and_by_organization(self, organization_id: uuid.UUID) -> list[ReportModel]:
        result = await self.session.execute(
            select(ReportModel).where(
                (ReportModel.is_global.is_(True)) | (ReportModel.organization_id == organization_id),
                ReportModel.is_active.is_(True),
                ReportModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())
