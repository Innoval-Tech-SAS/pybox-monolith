import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.repository_base import RepositoryBase
from receivables.reports.models.report_execution_model import ReportExecutionModel


class ReportExecutionRepository(RepositoryBase[ReportExecutionModel]):
    model_class = ReportExecutionModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_report(self, report_id: uuid.UUID) -> Sequence[ReportExecutionModel]:
        result = await self.session.execute(
            select(ReportExecutionModel)
            .where(ReportExecutionModel.report_id == report_id)
            .order_by(ReportExecutionModel.created_at.desc())
        )
        return result.scalars().all()
