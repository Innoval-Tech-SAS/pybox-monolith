from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from app_platform.schema_manager.services.dml_service import DmlService
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository
from receivables.segments.repository.segment_execution_repository import SegmentExecutionRepository
from receivables.segments.repository.segment_repository import SegmentRepository
from receivables.segments.services.segment_service import SegmentService


def get_segment_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> SegmentService:
    return SegmentService(
        segment_repo=SegmentRepository(session),
        execution_repo=SegmentExecutionRepository(session),
        dml_service=DmlService(session),
        portfolio_repo=PortfolioRepository(session),
    )


SegmentServiceDep = Annotated[SegmentService, Depends(get_segment_service)]
