from sqlalchemy.ext.asyncio import AsyncSession

from base.soft_delete_repository_base import SoftDeleteRepositoryBase
from organizations.models.organization_model import OrganizationModel


class OrganizationRepository(SoftDeleteRepositoryBase[OrganizationModel]):
    model_class = OrganizationModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)
