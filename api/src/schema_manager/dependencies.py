from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_main_session
from schema_manager.services.ddl_service import DdlService
from schema_manager.services.dml_service import DmlService
from schema_manager.services.inspector_service import InspectorService


def get_inspector_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> InspectorService:
    return InspectorService(session)


def get_dml_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> DmlService:
    return DmlService(session)


def get_ddl_service() -> DdlService:
    return DdlService()


InspectorServiceDep = Annotated[InspectorService, Depends(get_inspector_service)]
DmlServiceDep = Annotated[DmlService, Depends(get_dml_service)]
DdlServiceDep = Annotated[DdlService, Depends(get_ddl_service)]
