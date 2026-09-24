import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from identity.organizations.models.organization_membership_model import OrganizationMembershipModel


class OrganizationMembershipRepository(SoftDeleteRepositoryBase[OrganizationMembershipModel]):
    model_class = OrganizationMembershipModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[OrganizationMembershipModel]:
        result = await self.session.execute(
            select(OrganizationMembershipModel).where(
                OrganizationMembershipModel.user_id == user_id,
                OrganizationMembershipModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_by_user_id_including_deleted(self, user_id: uuid.UUID) -> list[OrganizationMembershipModel]:
        result = await self.session.execute(
            select(OrganizationMembershipModel).where(
                OrganizationMembershipModel.user_id == user_id,
            )
        )
        return list(result.scalars().all())

    async def get_by_user_ids(self, user_ids: list[uuid.UUID]) -> list[OrganizationMembershipModel]:
        if not user_ids:
            return []
        result = await self.session.execute(
            select(OrganizationMembershipModel).where(
                OrganizationMembershipModel.user_id.in_(user_ids),
                OrganizationMembershipModel.deleted_at.is_(None),
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

    async def soft_delete_by_organization(self, organization_id: uuid.UUID, deleted_at: datetime) -> list[uuid.UUID]:
        """Baja de las membresías vivas de la organización con el sello de la organización.
        Devuelve los ids de usuario afectados (para invalidar sus sesiones cacheadas)."""
        result = await self.session.execute(
            select(OrganizationMembershipModel.user_id).where(
                OrganizationMembershipModel.organization_id == organization_id,
                OrganizationMembershipModel.deleted_at.is_(None),
            )
        )
        user_ids = list(result.scalars().all())
        await self.soft_delete_where(
            OrganizationMembershipModel.organization_id == organization_id, deleted_at=deleted_at
        )
        return user_ids

    async def restore_by_organization(self, organization_id: uuid.UUID, deleted_at: datetime) -> list[uuid.UUID]:
        """Inverso de ``soft_delete_by_organization``: solo las membresías que cayeron con la
        organización, no las de miembros que ya habían sido removidos antes."""
        result = await self.session.execute(
            select(OrganizationMembershipModel.user_id).where(
                OrganizationMembershipModel.organization_id == organization_id,
                OrganizationMembershipModel.deleted_at == deleted_at,
            )
        )
        user_ids = list(result.scalars().all())
        await self.restore_where(
            OrganizationMembershipModel.organization_id == organization_id, deleted_at=deleted_at
        )
        return user_ids
