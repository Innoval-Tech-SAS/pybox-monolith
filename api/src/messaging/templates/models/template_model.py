import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel
from messaging.templates.enums.template_enums import TemplateChannel, TemplateStatus


class TemplateModel(AuditModel):

    __tablename__ = "plantillas"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        name="id",
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("entidades.id"),
        nullable=False,
        index=True,
        name="id_organizacion",
    )

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, name="nombre_plantilla"
    )

    channel: Mapped[TemplateChannel] = mapped_column(
        Enum(TemplateChannel), nullable=False, name="canal"
    )

    status: Mapped[TemplateStatus] = mapped_column(
        Enum(TemplateStatus),
        nullable=False,
        default=TemplateStatus.DRAFT,
        name="estado_plantilla",
    )

    body: Mapped[str] = mapped_column(Text, nullable=False, name="cuerpo")

    design: Mapped[str | None] = mapped_column(Text, nullable=True, name="diseno")

    subject: Mapped[str | None] = mapped_column(
        String(255), nullable=True, name="asunto"
    )

    sender_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True, name="nombre_remitente"
    )

    sender_email: Mapped[str | None] = mapped_column(
        String(255), nullable=True, name="email_remitente"
    )

    reply_to: Mapped[str | None] = mapped_column(
        String(255), nullable=True, name="responder_a"
    )
