import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.soft_delete_repository_base import SoftDeleteRepositoryBase
from organizations.models.organization_membership_model import OrganizationMembershipModel


class OrganizationMembershipRepository(SoftDeleteRepositoryBase[OrganizationMembershipModel]):
    model_class = OrganizationMembershipModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_user_id(self, user_id: int) -> list[OrganizationMembershipModel]:
        result = await self.session.execute(
            select(OrganizationMembershipModel).where(
                OrganizationMembershipModel.user_id == user_id,
                OrganizationMembershipModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_by_user_id_including_deleted(self, user_id: int) -> list[OrganizationMembershipModel]:
        result = await self.session.execute(
            select(OrganizationMembershipModel).where(
                OrganizationMembershipModel.user_id == user_id,
            )
        )
        return list(result.scalars().all())

    async def get_by_organization_id(self, org_id: uuid.UUID) -> list[OrganizationMembershipModel]:
        result = await self.session.execute(
            select(OrganizationMembershipModel).where(
                OrganizationMembershipModel.organization_id == org_id,
                OrganizationMembershipModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_by_organization_id_including_deleted(self, org_id: uuid.UUID) -> list[OrganizationMembershipModel]:
        result = await self.session.execute(
            select(OrganizationMembershipModel).where(
                OrganizationMembershipModel.organization_id == org_id,
            )
        )
        return list(result.scalars().all())
