import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from base.audit_model import AuditModel
from campaigns.enums.campaign_enums import CampaignStatus


class CampaignModel(AuditModel):

    __tablename__ = "campanias"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
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
        String(255), nullable=False, index=True, name="nombre_campania"
    )

    message: Mapped[str] = mapped_column(Text, nullable=False, name="mensaje")

    subject: Mapped[str | None] = mapped_column(String(255), nullable=True, name="asunto")

    channel: Mapped[str] = mapped_column(String(25), nullable=False, default="auto", name="canal")

    description: Mapped[str | None] = mapped_column(
        String(255), nullable=True, name="descripcion_campania"
    )

    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus),
        nullable=False,
        default=CampaignStatus.DRAFT,
        name="estado_campania",
    )

    total_recipients: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, name="total_destinatarios"
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, name="programado_para"
    )

    timezone: Mapped[str] = mapped_column(String(50), default="UTC", name="zona_horaria")

    fallback: Mapped[bool] = mapped_column(Boolean, default=True, name="fallback")
