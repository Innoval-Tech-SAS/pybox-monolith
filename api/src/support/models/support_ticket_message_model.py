import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from base.audit_model import AuditModel


class SupportTicketMessageModel(AuditModel):
    __tablename__ = "soporte_mensajes"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id"
    )
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("soporte_tickets.id", ondelete="CASCADE"),
        nullable=False,
        name="ticket_id",
        index=True,
    )
    sender_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False, name="remitente_id"
    )
    body: Mapped[str] = mapped_column(Text, nullable=False, name="cuerpo")
    is_internal: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, name="es_interno"
    )
