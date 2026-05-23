import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.repository_base import RepositoryBase
from users.enums.user_enums import PermissionEffect
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
