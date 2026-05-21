from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.repository_base import RepositoryBase
from ..models.role_assignment_model import RoleAssignmentModel


class RoleAssignmentRepository(RepositoryBase[RoleAssignmentModel]):
    model_class = RoleAssignmentModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_user_id(self, user_id: int) -> list[RoleAssignmentModel]:
        result = await self.session.execute(
            select(RoleAssignmentModel).where(RoleAssignmentModel.user_id == user_id)
        )
        return list(result.scalars().all())
