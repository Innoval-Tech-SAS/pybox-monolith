import uuid
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, WebSocket, status
from pydantic import ValidationError as PydanticValidationError

from identity.auth.dependencies import TokenPayload
from core.config.redis_config import RedisConfig
from core.database.redis import redis_client
from core.security.constants.cookie_constants import ACCESS_TOKEN_COOKIE
from core.security.services.auth_token_service import AuthTokenService
from core.security.utils.service_key_verifier import verify_n8n_service_key
from identity.users.schemas.user_session_schema import UserSession, mfa_verified_key, session_key

_sse_token_service = AuthTokenService()


def _resolve_stream_token(connection: Request | WebSocket) -> str:
    """El token de acceso de un stream (SSE/WebSocket) sale SOLO de la cookie httpOnly.

    Aceptarlo también por query string (`?token=`) lo dejaría en logs de acceso, proxies e
    historial del navegador; `EventSource` y `WebSocket` adjuntan la cookie solos."""
    token = connection.cookies.get(ACCESS_TOKEN_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")
    return token


def _subject_to_uuid(payload: TokenPayload) -> uuid.UUID:
    try:
        return uuid.UUID(str(payload["sub"]))
    except (KeyError, ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")


async def _load_session(user_id: uuid.UUID) -> UserSession:
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


async def _require_mfa_verified(session: UserSession) -> UserSession:
    """Exige que el segundo factor ya se haya superado en el login vigente.

    El token/cookie de acceso se emite completo desde el login (ver
    `AuthService._build_response`): sin este chequeo, el MFA solo bloquea la UI de
    React y cualquiera con la contraseña correcta tiene acceso completo a la API
    saltándose el segundo factor. `mfa_verified_key` lo setea
    `OnboardingService.verify_otp` al validar el código, y `_build_response` lo borra
    en cada login nuevo (no en refresh) para que un login nuevo siempre lo vuelva a
    exigir."""
    if session.mfa_enabled and not await redis_client.get(mfa_verified_key(session.user_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verificación de dos pasos pendiente.",
        )
    return session


async def get_session(payload: TokenPayload) -> UserSession:
    session = await _load_session(_subject_to_uuid(payload))
    return await _require_mfa_verified(session)


async def get_pending_mfa_session(payload: TokenPayload) -> UserSession:
    """Igual que `get_session` pero sin exigir el segundo factor.

    La usan exclusivamente los endpoints de onboarding (incluidos request/verify-otp):
    son justo los que deben quedar accesibles mientras el MFA sigue pendiente, ya sea
    porque el usuario todavía está completando su registro o porque está resolviendo
    el propio desafío de MFA."""
    return await _load_session(_subject_to_uuid(payload))


async def get_sse_session(request: Request) -> UserSession:
    resolved_token = _resolve_stream_token(request)
    try:
        payload = _sse_token_service.verify_token(resolved_token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")
    session = await _load_session(_subject_to_uuid(payload))
    return await _require_mfa_verified(session)


async def get_ws_session(websocket: WebSocket) -> UserSession:
    resolved_token = _resolve_stream_token(websocket)
    try:
        payload = _sse_token_service.verify_token(resolved_token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")
    session = await _load_session(_subject_to_uuid(payload))
    return await _require_mfa_verified(session)


async def require_n8n_service_key(x_service_key: Annotated[str | None, Header()] = None) -> None:
    """Gate de ruta para los endpoints internos que consume n8n (sin sesión de usuario)."""
    if not verify_n8n_service_key(x_service_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid service key")


CurrentSession = Annotated[UserSession, Depends(get_session)]
PendingMfaSession = Annotated[UserSession, Depends(get_pending_mfa_session)]
SSESession = Annotated[UserSession, Depends(get_sse_session)]
