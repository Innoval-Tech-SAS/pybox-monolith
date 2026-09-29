import uuid
from typing import Sequence

from sqlalchemy import select

from app_platform.support.models.support_ticket_message_model import (
    SupportTicketMessageModel,
)
from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase


class SupportMessageRepository(SoftDeleteRepositoryBase[SupportTicketMessageModel]):
    model_class = SupportTicketMessageModel

    async def get_by_ticket_id(
        self, ticket_id: uuid.UUID
    ) -> Sequence[SupportTicketMessageModel]:
        result = await self.session.execute(
            select(SupportTicketMessageModel)
            .where(SupportTicketMessageModel.ticket_id == ticket_id)
            .order_by(SupportTicketMessageModel.created_at.asc())
        )
        return result.scalars().all()
