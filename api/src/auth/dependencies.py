from typing import Annotated, Any, AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_main_session
from security.services.auth_token_service import AuthTokenService
from users.repository.user_repository import UserRepository
from users.repository.role_assignment_repository import RoleAssignmentRepository
from .services.auth_service import AuthService

_bearer = HTTPBearer()
_token_service = AuthTokenService()


def _get_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
) -> dict[str, Any]:
    from config.logger import logger
    logger.debug(f"[_get_token_payload] START — scheme={credentials.scheme!r} token_prefix={credentials.credentials[:30]!r}")
    try:
        payload = _token_service.verify_token(credentials.credentials)
        logger.debug(f"[_get_token_payload] END   — OK payload_keys={list(payload.keys())}")
        return payload
    except ValueError as error:
        logger.debug(f"[_get_token_payload] END   — REJECTED: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> AuthService:
    return AuthService(
        user_repository=UserRepository(session),
        role_assignment_repository=RoleAssignmentRepository(session),
    )


TokenPayload = Annotated[dict[str, Any], Depends(_get_token_payload)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
