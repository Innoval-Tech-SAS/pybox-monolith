from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_main_session
from organizations.repository.organization_membership_repository import OrganizationMembershipRepository
from organizations.repository.organization_repository import OrganizationRepository
from organizations.services.organization_service import OrganizationService
from security.dependencies import CurrentSession
from users.enums.user_enums import UserRole, UserScope
from users.repository.role_assignment_repository import RoleAssignmentRepository
from users.repository.user_repository import UserRepository
from users.schemas.user_session_schema import UserSession


async def get_admin_scope(session: CurrentSession) -> UserScope:
    if session.is_global and session.role == UserRole.ADMIN:
        return UserScope.GLOBAL
    for org_entry in session.orgs.values():
        if org_entry.role == UserRole.ADMIN:
            return UserScope.ORGANIZATION
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Se requiere rol de administrador",
    )


def get_organization_service(
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> OrganizationService:
    return OrganizationService(
        org_repo=OrganizationRepository(db),
        membership_repo=OrganizationMembershipRepository(db),
        role_assignment_repo=RoleAssignmentRepository(db),
        user_repo=UserRepository(db),
    )


AdminScopeDep = Annotated[UserScope, Depends(get_admin_scope)]
OrgServiceDep = Annotated[OrganizationService, Depends(get_organization_service)]
