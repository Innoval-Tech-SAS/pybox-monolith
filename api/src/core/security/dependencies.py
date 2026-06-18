import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from pydantic import ValidationError as PydanticValidationError

from identity.auth.dependencies import TokenPayload
from core.config.redis_config import RedisConfig
from core.database.redis import redis_client
from core.security.services.auth_token_service import AuthTokenService
from identity.users.schemas.user_session_schema import UserSession, session_key

_sse_token_service = AuthTokenService()


def _subject_to_uuid(payload: TokenPayload) -> uuid.UUID:
    try:
        return uuid.UUID(str(payload["sub"]))
    except (KeyError, ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")


async def get_session(payload: TokenPayload) -> UserSession:
    user_id = _subject_to_uuid(payload)
    key = session_key(user_id)
    try:
        session = await redis_client.get_json(key, UserSession)
    except PydanticValidationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tu sesión no es válida. Inicia sesión nuevamente.",
        )
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
    user_id = _subject_to_uuid(payload)
    key = session_key(user_id)
    try:
        session = await redis_client.get_json(key, UserSession)
    except PydanticValidationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tu sesión no es válida. Inicia sesión nuevamente.",
        )
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
    user_id = _subject_to_uuid(payload)
    key = session_key(user_id)
    try:
        session = await redis_client.get_json(key, UserSession)
    except PydanticValidationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tu sesión no es válida. Inicia sesión nuevamente.",
        )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada. Inicia sesión nuevamente.",
        )
    await redis_client.expire(key, RedisConfig.DEFAULT_TTL)
    return session


CurrentSession = Annotated[UserSession, Depends(get_session)]
SSESession = Annotated[UserSession, Depends(get_sse_session)]
