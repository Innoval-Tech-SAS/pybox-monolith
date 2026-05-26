import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.repository_base import RepositoryBase
from users.enums.user_enums import PermissionEffect, UserScope
from users.models.permission_assignment_model import PermissionAssignmentModel
from users.models.permission_model import PermissionModel


class PermissionAssignmentRepository(RepositoryBase[PermissionAssignmentModel]):
    model_class = PermissionAssignmentModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_overrides_for_user_org(
        self, user_id: int, organization_id: uuid.UUID
    ) -> list[tuple[str, PermissionEffect]]:
        result = await self.session.execute(
            select(PermissionModel.name, PermissionAssignmentModel.effect)
            .join(PermissionModel, PermissionAssignmentModel.permission_id == PermissionModel.id)
            .where(
                PermissionAssignmentModel.user_id == user_id,
                PermissionAssignmentModel.organization_id == organization_id,
                PermissionAssignmentModel.is_active.is_(True),
            )
        )
        return list(result.all())

    async def get_permission_by_name(self, name: str) -> PermissionModel | None:
        result = await self.session.execute(
            select(PermissionModel).where(PermissionModel.name == name, PermissionModel.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def get_assignment(
        self, user_id: int, permission_id: int, organization_id: uuid.UUID
    ) -> PermissionAssignmentModel | None:
        result = await self.session.execute(
            select(PermissionAssignmentModel).where(
                PermissionAssignmentModel.user_id == user_id,
                PermissionAssignmentModel.permission_id == permission_id,
                PermissionAssignmentModel.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_for_org(
        self,
        user_id: int,
        permission_id: int,
        organization_id: uuid.UUID,
        effect: PermissionEffect,
    ) -> PermissionAssignmentModel:
        existing = await self.get_assignment(user_id, permission_id, organization_id)
        if existing:
            existing.effect = effect
            existing.is_active = True
            return await self.update(existing)
        return await self.add(
            PermissionAssignmentModel(
                user_id=user_id,
                permission_id=permission_id,
                scope=UserScope.ORGANIZATION,
                organization_id=organization_id,
                effect=effect,
            )
        )

    async def delete_for_org(
        self, user_id: int, permission_id: int, organization_id: uuid.UUID
    ) -> bool:
        existing = await self.get_assignment(user_id, permission_id, organization_id)
        if not existing:
            return False
        await self.delete(existing)
        return True
