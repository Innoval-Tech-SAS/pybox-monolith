from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from messaging.templates.repositories.template_repository import TemplateRepository
from messaging.templates.services.template_service import TemplateService


def get_template_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> TemplateService:
    return TemplateService(
        template_repo=TemplateRepository(session),
    )


TemplateServiceDep = Annotated[TemplateService, Depends(get_template_service)]
