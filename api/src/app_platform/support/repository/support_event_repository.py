import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.repository_base import RepositoryBase
from app_platform.support.models.support_ticket_event_model import SupportTicketEventModel


class SupportEventRepository(RepositoryBase[SupportTicketEventModel]):
    model_class = SupportTicketEventModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_ticket_id(self, ticket_id: uuid.UUID) -> Sequence[SupportTicketEventModel]:
        result = await self.session.execute(
            select(SupportTicketEventModel)
            .where(SupportTicketEventModel.ticket_id == ticket_id)
            .order_by(SupportTicketEventModel.created_at.asc())
        )
        return result.scalars().all()
