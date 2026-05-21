from typing import Annotated

from fastapi import Depends, HTTPException, status
from config.api_router import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import TokenPayload
from database.database import get_main_session
from users.repository.user_repository import UserRepository
from users.schemas.user_schemas import UserProfile

router = APIRouter(prefix="/users", tags=["users"])

MainSession = Annotated[AsyncSession, Depends(get_main_session)]


@router.get("/me", response_model=UserProfile)
async def me(payload: TokenPayload, session: MainSession) -> UserProfile:
    user_id = int(payload["sub"])
    user = await UserRepository(session).get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

    return UserProfile.model_validate(user)
