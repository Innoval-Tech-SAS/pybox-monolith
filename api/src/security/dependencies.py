from typing import Annotated

from fastapi import Depends, HTTPException, status

from auth.dependencies import TokenPayload
from config.redis_config import RedisConfig
from database.redis import redis_client
from users.schemas.user_session_schema import UserSession, session_key


async def get_session(payload: TokenPayload) -> UserSession:
    user_id = int(payload["sub"])
    key = session_key(user_id)
    session = await redis_client.get_json(key, UserSession)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada. Inicia sesión nuevamente.",
        )
    await redis_client.expire(key, RedisConfig.DEFAULT_TTL)
    return session


CurrentSession = Annotated[UserSession, Depends(get_session)]
