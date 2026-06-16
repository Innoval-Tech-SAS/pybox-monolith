import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ENUM, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel
from platform.support.enums.support_enums import SupportTicketEventType


class SupportTicketEventModel(AuditModel):
    __tablename__ = "soporte_eventos"

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
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, name="usuario_id"
    )
    event_type: Mapped[SupportTicketEventType] = mapped_column(
        ENUM(SupportTicketEventType), nullable=False, name="tipo_evento"
    )
    from_value: Mapped[str | None] = mapped_column(String(100), nullable=True, name="valor_anterior")
    to_value: Mapped[str | None] = mapped_column(String(100), nullable=True, name="valor_nuevo")
