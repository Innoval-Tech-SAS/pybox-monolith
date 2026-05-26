import uuid
from typing import TYPE_CHECKING, Sequence

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from base.repository_base import RepositoryBase
from support.enums.support_enums import SupportTicketStatus
from support.models.support_ticket_model import SupportTicketModel
from users.enums.user_enums import UserRole, UserScope
from users.models.role_assignment_model import RoleAssignmentModel

if TYPE_CHECKING:
    from support.schemas.support_schemas import SupportFilter


class SupportTicketRepository(RepositoryBase[SupportTicketModel]):
    model_class = SupportTicketModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_filtered(self, f: "SupportFilter") -> Sequence[SupportTicketModel]:
        conditions = []
        if not f.include_resolved:
            conditions.append(SupportTicketModel.status != SupportTicketStatus.RESOLVED)
        if f.org_ids is not None:
            conditions.append(SupportTicketModel.organization_id.in_(f.org_ids))
        if f.created_by is not None:
            conditions.append(SupportTicketModel.created_by == f.created_by)
        result = await self.session.execute(
            select(SupportTicketModel).where(*conditions)
        )
        return result.scalars().all()

    async def find_least_loaded_cs_org(self, org_id: uuid.UUID) -> int | None:
        stmt = (
            select(RoleAssignmentModel.user_id)
            .outerjoin(
                SupportTicketModel,
                and_(
                    SupportTicketModel.assigned_to == RoleAssignmentModel.user_id,
                    SupportTicketModel.status != SupportTicketStatus.RESOLVED,
                ),
            )
            .where(
                RoleAssignmentModel.role == UserRole.CUSTOMER_SERVICE,
                RoleAssignmentModel.scope == UserScope.ORGANIZATION,
                RoleAssignmentModel.organization_id == org_id,
            )
            .group_by(RoleAssignmentModel.user_id)
            .order_by(func.count(SupportTicketModel.id).asc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_least_loaded_cs_global(self) -> int | None:
        stmt = (
            select(RoleAssignmentModel.user_id)
            .outerjoin(
                SupportTicketModel,
                and_(
                    SupportTicketModel.assigned_to == RoleAssignmentModel.user_id,
                    SupportTicketModel.status != SupportTicketStatus.RESOLVED,
                ),
            )
            .where(
                RoleAssignmentModel.role == UserRole.CUSTOMER_SERVICE,
                RoleAssignmentModel.scope == UserScope.GLOBAL,
            )
            .group_by(RoleAssignmentModel.user_id)
            .order_by(func.count(SupportTicketModel.id).asc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
