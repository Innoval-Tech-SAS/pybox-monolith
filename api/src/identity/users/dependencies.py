"""Dependencias de FastAPI para inyectar UserService y UserManagementService."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
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
from identity.users.services.user_management_service import UserManagementService
from identity.users.services.user_service import UserService


def get_user_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> UserService:
    return UserService(
        user_repo=UserRepository(session),
        org_repo=OrganizationRepository(session),
        membership_repo=OrganizationMembershipRepository(session),
        role_assignment_repo=RoleAssignmentRepository(session),
        permission_assignment_repo=PermissionAssignmentRepository(session),
        preferences_repo=UserPreferencesRepository(session),
    )


def get_user_management_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> UserManagementService:
    return UserManagementService(
        user_repo=UserRepository(session),
        role_assignment_repo=RoleAssignmentRepository(session),
        membership_repo=OrganizationMembershipRepository(session),
        permission_assignment_repo=PermissionAssignmentRepository(session),
    )


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
UserManagementServiceDep = Annotated[
    UserManagementService, Depends(get_user_management_service)
]
