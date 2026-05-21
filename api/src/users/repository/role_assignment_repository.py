from base.repository_base import RepositoryBase
from ..models.role_assignment_model import RoleAssignmentModel


class RoleAssignmentRepository(RepositoryBase[RoleAssignmentModel]):
    model_class = RoleAssignmentModel
