"""Mensaje intercambiado dentro de un ticket de soporte."""

import uuid

from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import BaseModel


class SupportTicketMessageModel(BaseModel):
    __tablename__ = "soporte_mensajes"

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("soporte_tickets.id", ondelete="CASCADE"),
        nullable=False,
        name="ticket_id",
        index=True,
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False,
        name="remitente_id",
        index=True,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False, name="cuerpo")
    is_internal: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, name="es_interno"
    )
