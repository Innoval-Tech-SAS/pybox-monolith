from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.api_router import APIRouter
from credits.schemas.my_credits_schemas import MyCreditResponse
from credits.services.my_credits_service import MyCreditsService
from database.database import get_main_session
from security.dependencies import CurrentSession
from security.policies import get_self_identity

router = APIRouter(prefix="/credits", tags=["my-credits"])


def get_my_credits_service(
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> MyCreditsService:
    return MyCreditsService(db)


@router.get("/my-credits", response_model=list[MyCreditResponse])
async def my_credits(
    session: CurrentSession,
    service: Annotated[MyCreditsService, Depends(get_my_credits_service)],
) -> list[MyCreditResponse]:
    doc_type, doc_number = get_self_identity(session)
    return await service.get_my_credits(doc_type, doc_number)
