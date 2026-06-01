from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_main_session
from databases.services.database_descriptor_service import DatabaseDescriptorService
from databases.services.dynamic_query_service import DynamicQueryService
from databases.services.schema_alteration_service import SchemaAlterationService


def get_descriptor_service() -> DatabaseDescriptorService:
    return DatabaseDescriptorService()


def get_dynamic_query_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> DynamicQueryService:
    return DynamicQueryService(session)


def get_schema_alteration_service() -> SchemaAlterationService:
    return SchemaAlterationService()


DescriptorServiceDep = Annotated[DatabaseDescriptorService, Depends(get_descriptor_service)]
DynamicQueryServiceDep = Annotated[DynamicQueryService, Depends(get_dynamic_query_service)]
SchemaAlterationServiceDep = Annotated[SchemaAlterationService, Depends(get_schema_alteration_service)]
