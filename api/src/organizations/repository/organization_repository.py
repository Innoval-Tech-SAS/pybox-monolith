from ..models.organization_model import OrganizationModel

from base.repository_base import RepositoryBase
from database.database import db


class OrganizationRepository(RepositoryBase):
    def __init__(self):
        super().__init__(db, OrganizationModel)
