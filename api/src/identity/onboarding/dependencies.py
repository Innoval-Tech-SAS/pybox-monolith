import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.support.services.support_service import SupportService
from core.database.database import get_main_session
from identity.onboarding.services.onboarding_service import OnboardingService
from identity.organizations.models.organization_model import OrganizationModel
from identity.organizations.repository.organization_membership_repository import OrganizationMembershipRepository
from identity.organizations.repository.organization_repository import OrganizationRepository
from core.security.dependencies import CurrentSession, get_pending_mfa_session, get_session
from identity.users.enums.user_enums import UserScope
from identity.users.repository.permission_assignment_repository import PermissionAssignmentRepository
from identity.users.repository.role_assignment_repository import RoleAssignmentRepository
from identity.users.repository.user_preferences_repository import UserPreferencesRepository
from identity.users.repository.user_repository import UserRepository
from identity.users.schemas.user_session_schema import UserSession
from identity.users.services.user_service import UserService
from receivables.contact_methods.dependencies import get_self_service_contact_service


def _scope_from_session(session: UserSession) -> UserScope:
    if session.is_global:
        return UserScope.GLOBAL
    if session.orgs or session.scope == UserScope.ORGANIZATION:
        return UserScope.ORGANIZATION
    return UserScope.SELF


async def _org_from_session(session: UserSession, db: AsyncSession) -> OrganizationModel | None:
    if not session.orgs:
        return None
    first_org_id = next(iter(session.orgs))
    return await OrganizationRepository(db).get_by_id(uuid.UUID(first_org_id))


def get_current_scope(session: Annotated[UserSession, Depends(get_session)]) -> UserScope:
    return _scope_from_session(session)


async def get_current_org(
    session: Annotated[UserSession, Depends(get_session)],
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> OrganizationModel | None:
    return await _org_from_session(session, db)


def get_current_scope_pending_mfa(session: Annotated[UserSession, Depends(get_pending_mfa_session)]) -> UserScope:
    """Variante de `get_current_scope` para endpoints de onboarding (ver
    `PendingMfaSession` en core/security/dependencies.py): el segundo factor todavía
    puede estar pendiente en ese punto del flujo."""
    return _scope_from_session(session)


async def get_current_org_pending_mfa(
    session: Annotated[UserSession, Depends(get_pending_mfa_session)],
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> OrganizationModel | None:
    return await _org_from_session(session, db)


def get_onboarding_service(
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> OnboardingService:
    user_repo = UserRepository(db)
    org_repo = OrganizationRepository(db)
    membership_repo = OrganizationMembershipRepository(db)
    role_repo = RoleAssignmentRepository(db)
    user_service = UserService(
        user_repo=user_repo,
        org_repo=org_repo,
        membership_repo=membership_repo,
        role_assignment_repo=role_repo,
        permission_assignment_repo=PermissionAssignmentRepository(db),
        preferences_repo=UserPreferencesRepository(db),
    )
    return OnboardingService(
        session=db,
        user_repo=user_repo,
        org_repo=org_repo,
        membership_repo=membership_repo,
        role_repo=role_repo,
        user_service=user_service,
        support_service=SupportService(db),
        self_service_contact_service=get_self_service_contact_service(db),
    )


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
PendingMfaScope = Annotated[UserScope, Depends(get_current_scope_pending_mfa)]
PendingMfaOrg = Annotated[OrganizationModel | None, Depends(get_current_org_pending_mfa)]
OnboardingServiceDep = Annotated[OnboardingService, Depends(get_onboarding_service)]
