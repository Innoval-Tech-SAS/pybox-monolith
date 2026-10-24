"""Acceso a datos del historial de eventos de un ticket de soporte."""

import uuid
from typing import Sequence

from sqlalchemy import select

from app_platform.support.models.support_ticket_event_model import (
    SupportTicketEventModel,
)
from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from identity.users.models.user_model import UserModel


class SupportEventRepository(SoftDeleteRepositoryBase[SupportTicketEventModel]):
    model_class = SupportTicketEventModel

    async def get_by_ticket_id(
        self, ticket_id: uuid.UUID
    ) -> Sequence[tuple[SupportTicketEventModel, str]]:
        """Devuelve cada evento junto al nombre del usuario que lo generó (join
        explícito por columnas, no relationship: el audit log solo necesita el
        nombre, cargar el UserModel completo por evento sería over-fetching)."""
        result = await self.session.execute(
            select(SupportTicketEventModel, UserModel.firstname, UserModel.lastname)
            .join(UserModel, UserModel.id == SupportTicketEventModel.user_id)
            .where(SupportTicketEventModel.ticket_id == ticket_id)
            .order_by(SupportTicketEventModel.created_at.asc())
        )
        return [
            (event, f"{firstname.strip()} {lastname}")
            for event, firstname, lastname in result.all()
        ]
