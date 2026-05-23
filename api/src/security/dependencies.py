from typing import Annotated

from fastapi import Depends, HTTPException, status

from auth.dependencies import TokenPayload
from database.redis import redis_client
from users.schemas.user_session_schema import UserSession


async def get_session(payload: TokenPayload) -> UserSession:
    user_id = int(payload["sub"])
    session = await redis_client.get_json(f"session:{user_id}", UserSession)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada. Inicia sesión nuevamente.",
        )
    return session


CurrentSession = Annotated[UserSession, Depends(get_session)]
