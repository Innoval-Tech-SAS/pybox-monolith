import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Identity, Integer, String
from sqlalchemy.dialects.postgresql import ENUM, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from base.audit_model import AuditModel
from support.enums.support_enums import SupportCaseType, SupportTicketStatus


class SupportTicketModel(AuditModel):
    __tablename__ = "soporte_tickets"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    ticket_number: Mapped[int] = mapped_column(Integer, Identity(start=1), unique=True, nullable=False, name="numero_ticket")
    case_type: Mapped[SupportCaseType] = mapped_column(
        ENUM(SupportCaseType), nullable=False, name="tipo_caso"
    )
    status: Mapped[SupportTicketStatus] = mapped_column(
        ENUM(SupportTicketStatus),
        nullable=False,
        default=SupportTicketStatus.OPEN,
        name="estado",
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("entidades.id"), nullable=False, name="id_entidad"
    )
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False, name="creado_por"
    )
    assigned_to: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=True, name="asignado_a"
    )
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True, name="notas")
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, name="resuelto_en"
    )
