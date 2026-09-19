from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from app_platform.countries.repository.country_repository import CountryRepository
from app_platform.countries.services.country_service import CountryService


def get_country_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> CountryService:
    return CountryService(CountryRepository(session))


CountryServiceDep = Annotated[CountryService, Depends(get_country_service)]
