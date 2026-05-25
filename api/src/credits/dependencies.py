from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from credits.services.my_credits_service import MyCreditsService
from database.database import get_main_session


def get_my_credits_service(
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> MyCreditsService:
    return MyCreditsService(db)


MyCreditsServiceDep = Annotated[MyCreditsService, Depends(get_my_credits_service)]
