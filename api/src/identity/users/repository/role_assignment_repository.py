import uuid
from datetime import datetime

from sqlalchemy import select

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase

from ..enums.user_enums import UserRole, UserScope
from ..models.role_assignment_model import RoleAssignmentModel


class RoleAssignmentRepository(SoftDeleteRepositoryBase[RoleAssignmentModel]):
    model_class = RoleAssignmentModel

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[RoleAssignmentModel]:
        result = await self.session.execute(
            select(RoleAssignmentModel).where(
                RoleAssignmentModel.user_id == user_id,
                RoleAssignmentModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_pending_org_admin(
        self, user_id: uuid.UUID
    ) -> RoleAssignmentModel | None:
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

    async def get_by_user_ids(
        self, user_ids: list[uuid.UUID]
    ) -> list[RoleAssignmentModel]:
        if not user_ids:
            return []
        result = await self.session.execute(
            select(RoleAssignmentModel).where(
                RoleAssignmentModel.user_id.in_(user_ids),
                RoleAssignmentModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_global_user_ids(self, user_ids: list[uuid.UUID]) -> set[uuid.UUID]:
        if not user_ids:
            return set()
        result = await self.session.execute(
            select(RoleAssignmentModel.user_id).where(
                RoleAssignmentModel.user_id.in_(user_ids),
                RoleAssignmentModel.scope == UserScope.GLOBAL,
                RoleAssignmentModel.deleted_at.is_(None),
            )
        )
        return set(result.scalars().all())

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

    async def soft_delete_by_organization(
        self, organization_id: uuid.UUID, deleted_at: datetime
    ) -> None:
        """Baja de los roles que los usuarios tenían en la organización (misma
        cascada que sus membresías): quien no tenga otro rol queda sin
        organización."""
        await self.soft_delete_where(
            RoleAssignmentModel.organization_id == organization_id,
            deleted_at=deleted_at,
        )

    async def restore_by_organization(
        self, organization_id: uuid.UUID, deleted_at: datetime
    ) -> None:
        await self.restore_where(
            RoleAssignmentModel.organization_id == organization_id,
            deleted_at=deleted_at,
        )
