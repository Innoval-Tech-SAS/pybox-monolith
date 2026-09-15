import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from ..enums.user_enums import UserRole, UserScope
from ..models.role_assignment_model import RoleAssignmentModel


class RoleAssignmentRepository(SoftDeleteRepositoryBase[RoleAssignmentModel]):
    model_class = RoleAssignmentModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[RoleAssignmentModel]:
        result = await self.session.execute(
            select(RoleAssignmentModel).where(
                RoleAssignmentModel.user_id == user_id,
                RoleAssignmentModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_pending_org_admin(self, user_id: uuid.UUID) -> RoleAssignmentModel | None:
        result = await self.session.execute(
            select(RoleAssignmentModel).where(
                RoleAssignmentModel.user_id == user_id,
                RoleAssignmentModel.role == UserRole.ADMIN,
                RoleAssignmentModel.scope == UserScope.ORGANIZATION,
                RoleAssignmentModel.organization_id.is_(None),
                RoleAssignmentModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_ids(self, user_ids: list[uuid.UUID]) -> list[RoleAssignmentModel]:
        if not user_ids:
            return []
        result = await self.session.execute(
            select(RoleAssignmentModel).where(
                RoleAssignmentModel.user_id.in_(user_ids),
                RoleAssignmentModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_admin_org_ids(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        result = await self.session.execute(
            select(RoleAssignmentModel.organization_id).where(
                RoleAssignmentModel.user_id == user_id,
                RoleAssignmentModel.role == UserRole.ADMIN,
                RoleAssignmentModel.scope == UserScope.ORGANIZATION,
                RoleAssignmentModel.organization_id.is_not(None),
                RoleAssignmentModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())
