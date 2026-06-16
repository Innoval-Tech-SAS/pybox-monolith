import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from identity.onboarding.services.onboarding_service import OnboardingService
from identity.organizations.models.organization_model import OrganizationModel
from identity.organizations.repository.organization_repository import OrganizationRepository
from core.security.dependencies import CurrentSession, get_session
from identity.users.enums.user_enums import UserScope
from identity.users.schemas.user_session_schema import UserSession


def get_current_scope(
    session: Annotated[UserSession, Depends(get_session)],
) -> UserScope:
    if session.is_global:
        return UserScope.GLOBAL
    if session.orgs or session.scope == UserScope.ORGANIZATION:
        return UserScope.ORGANIZATION
    return UserScope.SELF


async def get_current_org(
    session: Annotated[UserSession, Depends(get_session)],
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> OrganizationModel | None:
    if not session.orgs:
        return None
    first_org_id = next(iter(session.orgs))
    return await OrganizationRepository(db).get_by_id(uuid.UUID(first_org_id))


def get_onboarding_service(
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> OnboardingService:
    return OnboardingService(db)


async def require_onboarding_complete(
    session: Annotated[UserSession, Depends(get_session)],
    scope: Annotated[UserScope, Depends(get_current_scope)],
    org: Annotated[OrganizationModel | None, Depends(get_current_org)],
    service: Annotated[OnboardingService, Depends(get_onboarding_service)],
) -> None:
    onboarding_status = await service.get_status(session.user_id, scope, org)
    if not onboarding_status.is_complete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Onboarding incompleto",
                "missing_steps": onboarding_status.missing_steps,
            },
        )


CurrentScope = Annotated[UserScope, Depends(get_current_scope)]
CurrentOrg = Annotated[OrganizationModel | None, Depends(get_current_org)]
OnboardingServiceDep = Annotated[OnboardingService, Depends(get_onboarding_service)]
