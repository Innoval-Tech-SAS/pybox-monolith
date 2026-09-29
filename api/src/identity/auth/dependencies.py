"""Dependencias de FastAPI para autenticación: token de sesión y AuthService."""

from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.config.logger import logger
from core.database.database import get_main_session
from core.security.constants.cookie_constants import ACCESS_TOKEN_COOKIE
from core.security.services.auth_token_service import AuthTokenService
from identity.organizations.repository.organization_membership_repository import (
    OrganizationMembershipRepository,
)
from identity.organizations.repository.organization_repository import (
    OrganizationRepository,
)
from identity.users.repository.permission_assignment_repository import (
    PermissionAssignmentRepository,
)
from identity.users.repository.role_assignment_repository import (
    RoleAssignmentRepository,
)
from identity.users.repository.user_preferences_repository import (
    UserPreferencesRepository,
)
from identity.users.repository.user_repository import UserRepository
from identity.users.services.user_service import UserService

from .services.auth_service import AuthService

# auto_error=False: la cookie httpOnly tiene prioridad; el header Authorization
# queda como fallback (clientes que no manejan cookies, ej. API/mobile clients).
_bearer = HTTPBearer(auto_error=False)
_token_service = AuthTokenService()


def _get_token_payload(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer)
    ] = None,
) -> dict[str, Any]:
    token = request.cookies.get(ACCESS_TOKEN_COOKIE) or (
        credentials.credentials if credentials else None
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada. Inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = _token_service.verify_token(token)
        logger.debug("[auth] token_check | result=ok user_id=%s", payload.get("sub"))
        return payload
    except ValueError as error:
        logger.debug(
            "[auth] token_check | result=rejected error=%s", type(error).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> AuthService:
    user_repo = UserRepository(session)
    role_assignment_repo = RoleAssignmentRepository(session)
    user_service = UserService(
        user_repo=user_repo,
        org_repo=OrganizationRepository(session),
        membership_repo=OrganizationMembershipRepository(session),
        role_assignment_repo=role_assignment_repo,
        permission_assignment_repo=PermissionAssignmentRepository(session),
        preferences_repo=UserPreferencesRepository(session),
    )
    return AuthService(
        user_repository=user_repo,
        role_assignment_repository=role_assignment_repo,
        user_service=user_service,
        session=session,
    )


TokenPayload = Annotated[dict[str, Any], Depends(_get_token_payload)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
