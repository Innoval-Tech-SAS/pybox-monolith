import uuid
from typing import Sequence

from fastapi import HTTPException, status

from organizations.models.organization_membership_model import OrganizationMembershipModel
from organizations.models.organization_model import OrganizationModel
from organizations.repository.organization_membership_repository import OrganizationMembershipRepository
from organizations.repository.organization_repository import OrganizationRepository
from organizations.schemas.organization_schemas import OrganizationCreate, OrganizationUpdate
from users.enums.user_enums import UserRole, UserScope
from users.models.role_assignment_model import RoleAssignmentModel
from users.repository.role_assignment_repository import RoleAssignmentRepository


class OrganizationService:
    def __init__(
        self,
        org_repo: OrganizationRepository,
        membership_repo: OrganizationMembershipRepository,
        role_assignment_repo: RoleAssignmentRepository,
    ):
        self.org_repo = org_repo
        self.membership_repo = membership_repo
        self.role_assignment_repo = role_assignment_repo

    # ── Queries ──────────────────────────────────────────────────────────────

    async def get_all(self) -> Sequence[OrganizationModel]:
        return await self.org_repo.get_all()

    async def get_for_user(self, user_id: int, scope: UserScope) -> Sequence[OrganizationModel]:
        if scope == UserScope.GLOBAL:
            return await self.org_repo.get_all()
        if scope == UserScope.ORGANIZATION:
            memberships = await self.membership_repo.get_by_user_id(user_id)
            org_ids = [m.organization_id for m in memberships]
            return await self.org_repo.get_by_ids(org_ids)
        return []

    async def get_by_id(self, org_id: uuid.UUID) -> OrganizationModel:
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organización no encontrada")
        return org

    # ── Ownership helper ─────────────────────────────────────────────────────

    async def _assert_admin_of_org(self, user_id: int, org_id: uuid.UUID) -> None:
        admin_org_ids = await self.role_assignment_repo.get_admin_org_ids(user_id)
        if org_id not in admin_org_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para gestionar esta organización",
            )

    # ── Write operations ─────────────────────────────────────────────────────

    async def create_organization(
        self,
        data: OrganizationCreate,
        created_by_user_id: int,
        scope: UserScope,
    ) -> OrganizationModel:
        org = OrganizationModel(**data.model_dump())
        org = await self.org_repo.add(org)

        if scope == UserScope.ORGANIZATION:
            membership = OrganizationMembershipModel(
                user_id=created_by_user_id,
                organization_id=org.id,
                created_by=created_by_user_id,
            )
            await self.membership_repo.add(membership)

            # Promote pending role assignment (org_id=NULL) or create a new one
            pending = await self.role_assignment_repo.get_pending_org_admin(created_by_user_id)
            if pending:
                pending.organization_id = org.id
                await self.role_assignment_repo.update(pending)
            else:
                assignment = RoleAssignmentModel(
                    user_id=created_by_user_id,
                    role=UserRole.ADMIN,
                    scope=UserScope.ORGANIZATION,
                    organization_id=org.id,
                )
                await self.role_assignment_repo.add(assignment)

        return org

    async def update_organization(
        self,
        org_id: uuid.UUID,
        data: OrganizationUpdate,
        requesting_user_id: int,
        scope: UserScope,
    ) -> OrganizationModel:
        if scope == UserScope.ORGANIZATION:
            await self._assert_admin_of_org(requesting_user_id, org_id)

        org = await self.get_by_id(org_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(org, field, value)

        return await self.org_repo.update(org)

    async def delete_organization(
        self,
        org_id: uuid.UUID,
        requesting_user_id: int,
        scope: UserScope,
    ) -> None:
        if scope == UserScope.ORGANIZATION:
            await self._assert_admin_of_org(requesting_user_id, org_id)

        await self.get_by_id(org_id)  # raises 404 if not found

        memberships = await self.membership_repo.get_by_organization_id(org_id)
        for membership in memberships:
            await self.membership_repo.delete(membership)

        org = await self.org_repo.get_by_id(org_id)
        await self.org_repo.delete(org)

    # ── Soft-delete cascade (called from UserService) ─────────────────────────

    async def soft_delete_organization(self, org_id: uuid.UUID) -> None:
        memberships = await self.membership_repo.get_by_organization_id(org_id)
        for membership in memberships:
            await self.membership_repo.delete(membership)

        org = await self.org_repo.get_by_id(org_id)
        if org is not None:
            await self.org_repo.delete(org)

    async def restore_organization(self, org_id: uuid.UUID) -> OrganizationModel | None:
        org = await self.org_repo.get_by_id_including_deleted(org_id)
        if org is None or org.deleted_at is None:
            return org

        await self.org_repo.restore(org)

        memberships = await self.membership_repo.get_by_organization_id_including_deleted(org_id)
        for membership in memberships:
            if membership.deleted_at is not None:
                await self.membership_repo.restore(membership)

        return org
