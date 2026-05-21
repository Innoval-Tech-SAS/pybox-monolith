from typing import Annotated, Any, cast

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import TokenPayload
from database.database import get_main_session
from onboarding.services.onboarding_service import OnboardingService
from organizations.models.organization_model import OrganizationModel
from organizations.repository.organization_repository import OrganizationRepository
from organizations.repository.organization_membership_repository import (
    OrganizationMembershipRepository,
)
from users.enums.user_enums import UserScope
from users.models.user_model import UserModel
from users.repository.role_assignment_repository import RoleAssignmentRepository
from users.repository.user_repository import UserRepository


async def get_current_user(
    payload: TokenPayload,
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> UserModel:
    user_id = payload["sub"]
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado"
        )
    return user


async def get_current_scope(
    payload: TokenPayload,
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> UserScope:
    user_id = payload["sub"]
    repo = RoleAssignmentRepository(session)
    assignments = await repo.get_by_user_id(user_id)
    if not assignments:
        return UserScope.SELF
    # Primary scope: ORGANIZATION takes priority over SELF
    scopes = {a.scope for a in assignments}
    if UserScope.ORGANIZATION in scopes:
        return UserScope.ORGANIZATION
    return UserScope.SELF


async def get_current_org(
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> OrganizationModel | None:
    memberships = await OrganizationMembershipRepository(session).get_by_user_id(
        cast(int, user.id)
    )
    if not memberships:
        return None
    return await OrganizationRepository(session).get_by_id(
        memberships[0].organization_id
    )


def get_onboarding_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> OnboardingService:
    return OnboardingService(session)


async def require_onboarding_complete(
    user: Annotated[UserModel, Depends(get_current_user)],
    scope: Annotated[UserScope, Depends(get_current_scope)],
    org: Annotated[OrganizationModel | None, Depends(get_current_org)],
    service: Annotated[OnboardingService, Depends(get_onboarding_service)],
) -> None:
    onboarding_status = service.get_status(user, scope, org)
    if not onboarding_status.is_complete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Onboarding incompleto",
                "missing_steps": onboarding_status.missing_steps,
            },
        )


CurrentUser = Annotated[UserModel, Depends(get_current_user)]
CurrentScope = Annotated[UserScope, Depends(get_current_scope)]
CurrentOrg = Annotated[OrganizationModel | None, Depends(get_current_org)]
OnboardingServiceDep = Annotated[OnboardingService, Depends(get_onboarding_service)]
