from sqlalchemy.ext.asyncio import AsyncSession

from base.repository_base import RepositoryBase
from organizations.models.organization_model import OrganizationModel


class OrganizationRepository(RepositoryBase[OrganizationModel]):
    model_class = OrganizationModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)
