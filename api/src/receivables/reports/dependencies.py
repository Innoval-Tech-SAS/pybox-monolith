from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from app_platform.schema_manager.services.dml_service import DmlService
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository
from receivables.reports.repository.report_execution_repository import ReportExecutionRepository
from receivables.reports.repository.report_repository import ReportRepository
from receivables.reports.services.report_service import ReportService


def get_report_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> ReportService:
    return ReportService(
        report_repo=ReportRepository(session),
        execution_repo=ReportExecutionRepository(session),
        dml_service=DmlService(session),
        portfolio_repo=PortfolioRepository(session),
    )


ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]
