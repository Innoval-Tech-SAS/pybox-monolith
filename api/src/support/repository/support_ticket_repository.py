import uuid
from typing import TYPE_CHECKING, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.repository_base import RepositoryBase
from support.enums.support_enums import SupportTicketStatus
from support.models.support_ticket_model import SupportTicketModel

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
