"""Dependencias de FastAPI para inyectar TemplateService y TemplateVariableService."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.schema_manager.services.inspector_service import InspectorService
from core.database.database import get_main_session
from messaging.templates.repository.template_repository import TemplateRepository
from messaging.templates.services.template_service import TemplateService
from messaging.templates.services.template_variable_service import (
    TemplateVariableService,
)
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository


def get_template_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> TemplateService:
    return TemplateService(
        template_repo=TemplateRepository(session),
        portfolio_repo=PortfolioRepository(session),
    )


def get_template_variable_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> TemplateVariableService:
    return TemplateVariableService(InspectorService(session))


TemplateServiceDep = Annotated[TemplateService, Depends(get_template_service)]
TemplateVariableServiceDep = Annotated[
    TemplateVariableService, Depends(get_template_variable_service)
]
