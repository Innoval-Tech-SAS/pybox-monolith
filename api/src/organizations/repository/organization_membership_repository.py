from uuid import UUID

from base.repository_base import RepositoryBase
from database.database import db
from organizations.models.organization_membership_model import (
    OrganizationMembershipModel,
)


class OrganizationMembershipRepository(RepositoryBase[OrganizationMembershipModel]):
    def __init__(self):
        super().__init__(db, OrganizationMembershipModel)

    def get_by_user_and_organization(
        self,
        user_id: UUID,
        organization_id: UUID,
    ) -> OrganizationMembershipModel | None:
        with self.db.get_session() as session:
            return (
                session.query(self.model_class)
                .filter_by(user_id=user_id, organization_id=organization_id)
                .first()
            )

    def list_by_user(self, user_id: UUID) -> list[OrganizationMembershipModel]:
        with self.db.get_session() as session:
            return session.query(self.model_class).filter_by(user_id=user_id).all()
