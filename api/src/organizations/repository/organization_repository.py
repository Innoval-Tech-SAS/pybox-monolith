import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.soft_delete_repository_base import SoftDeleteRepositoryBase
from organizations.models.organization_model import OrganizationModel


class OrganizationRepository(SoftDeleteRepositoryBase[OrganizationModel]):
    model_class = OrganizationModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_ids(self, ids: list[uuid.UUID]) -> Sequence[OrganizationModel]:
        if not ids:
            return []
        result = await self.session.execute(
            select(OrganizationModel).where(
                OrganizationModel.id.in_(ids),
                OrganizationModel.deleted_at.is_(None),
            )
        )
        return result.scalars().all()
