from typing import Annotated

from fastapi import Depends, HTTPException, Query, status

from identity.auth.dependencies import TokenPayload
from core.config.redis_config import RedisConfig
from core.database.redis import redis_client
from core.security.services.auth_token_service import AuthTokenService
from identity.users.schemas.user_session_schema import UserSession, session_key

_sse_token_service = AuthTokenService()


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


async def get_sse_session(token: Annotated[str, Query()]) -> UserSession:
    try:
        payload = _sse_token_service.verify_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")
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


async def get_ws_session(token: str) -> UserSession:
    try:
        payload = _sse_token_service.verify_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")
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
SSESession = Annotated[UserSession, Depends(get_sse_session)]
