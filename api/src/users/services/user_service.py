from organizations.repository.organization_membership_repository import OrganizationMembershipRepository
from organizations.repository.organization_repository import OrganizationRepository
from organizations.services.organization_service import OrganizationService
from users.models.user_model import UserModel
from users.repository.role_assignment_repository import RoleAssignmentRepository
from users.repository.user_repository import UserRepository


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        org_repo: OrganizationRepository,
        membership_repo: OrganizationMembershipRepository,
        role_assignment_repo: RoleAssignmentRepository,
    ):
        self.user_repo = user_repo
        self.membership_repo = membership_repo
        self.role_assignment_repo = role_assignment_repo
        self._org_service = OrganizationService(org_repo, membership_repo, role_assignment_repo)

    async def soft_delete_user(self, user_id: int) -> None:
        admin_org_ids = await self.role_assignment_repo.get_admin_org_ids(user_id)

        # Cascade: delete orgs where this user is admin (takes their memberships with them)
        for org_id in admin_org_ids:
            await self._org_service.soft_delete_organization(org_id)

        # Soft delete user's remaining memberships in orgs they didn't own
        remaining_memberships = await self.membership_repo.get_by_user_id(user_id)
        for membership in remaining_memberships:
            if membership.organization_id not in admin_org_ids:
                await self.membership_repo.delete(membership)

        user = await self.user_repo.get_by_id(user_id)
        if user is not None:
            await self.user_repo.delete(user)

    async def restore_user(self, user_id: int) -> UserModel | None:
        user = await self.user_repo.get_by_id_including_deleted(user_id)
        if user is None or user.deleted_at is None:
            return user

        await self.user_repo.restore(user)

        admin_org_ids = await self.role_assignment_repo.get_admin_org_ids(user_id)

        # Cascade: restore orgs where this user is admin (and their memberships)
        for org_id in admin_org_ids:
            await self._org_service.restore_organization(org_id)

        # Restore user's memberships in orgs they didn't own
        all_memberships = await self.membership_repo.get_by_user_id_including_deleted(user_id)
        for membership in all_memberships:
            if membership.organization_id not in admin_org_ids and membership.deleted_at is not None:
                await self.membership_repo.restore(membership)

        return user
