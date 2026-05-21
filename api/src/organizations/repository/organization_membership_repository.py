from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.repository_base import RepositoryBase
from organizations.models.organization_membership_model import OrganizationMembershipModel


class OrganizationMembershipRepository(RepositoryBase[OrganizationMembershipModel]):
    model_class = OrganizationMembershipModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_user_id(self, user_id: int) -> list[OrganizationMembershipModel]:
        result = await self.session.execute(
            select(OrganizationMembershipModel).where(
                OrganizationMembershipModel.user_id == user_id
            )
        )
        return list(result.scalars().all())
