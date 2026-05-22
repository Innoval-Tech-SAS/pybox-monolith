from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_main_session
from onboarding.dependencies import CurrentUser
from organizations.repository.organization_membership_repository import OrganizationMembershipRepository
from organizations.repository.organization_repository import OrganizationRepository
from organizations.services.organization_service import OrganizationService
from users.enums.user_enums import UserRole, UserScope
from users.models.role_assignment_model import RoleAssignmentModel
from users.repository.role_assignment_repository import RoleAssignmentRepository


async def get_admin_assignment(
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> RoleAssignmentModel:
    """
    Verifica que el usuario autenticado tenga rol ADMIN.
    Devuelve su RoleAssignment de mayor jerarquía (GLOBAL > ORGANIZATION).
    """
    repo = RoleAssignmentRepository(session)
    assignments = await repo.get_by_user_id(user.id)
    admin_assignments = [a for a in assignments if a.role == UserRole.ADMIN]

    if not admin_assignments:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador",
        )

    # GLOBAL tiene prioridad sobre ORGANIZATION
    global_admin = next((a for a in admin_assignments if a.scope == UserScope.GLOBAL), None)
    if global_admin:
        return global_admin

    return admin_assignments[0]


def get_organization_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> OrganizationService:
    return OrganizationService(
        org_repo=OrganizationRepository(session),
        membership_repo=OrganizationMembershipRepository(session),
        role_assignment_repo=RoleAssignmentRepository(session),
    )


AdminAssignmentDep = Annotated[RoleAssignmentModel, Depends(get_admin_assignment)]
OrgServiceDep = Annotated[OrganizationService, Depends(get_organization_service)]
