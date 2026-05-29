from typing import Annotated, Any, AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_main_session
from organizations.repository.organization_membership_repository import OrganizationMembershipRepository
from organizations.repository.organization_repository import OrganizationRepository
from security.services.auth_token_service import AuthTokenService
from users.repository.permission_assignment_repository import PermissionAssignmentRepository
from users.repository.role_assignment_repository import RoleAssignmentRepository
from users.repository.user_preferences_repository import UserPreferencesRepository
from users.repository.user_repository import UserRepository
from users.services.user_service import UserService
from .services.auth_service import AuthService

_bearer = HTTPBearer()
_token_service = AuthTokenService()


def _get_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
) -> dict[str, Any]:
    from config.logger import logger
    logger.debug("[auth] token_check | scheme=%s", credentials.scheme)
    try:
        payload = _token_service.verify_token(credentials.credentials)
        logger.debug("[auth] token_check | result=ok user_id=%s", payload.get("sub"))
        return payload
    except ValueError as error:
        logger.debug("[auth] token_check | result=rejected error=%s", type(error).__name__)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        )


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
    )


TokenPayload = Annotated[dict[str, Any], Depends(_get_token_payload)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
