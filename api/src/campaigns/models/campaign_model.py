import uuid
from datetime import datetime

from sqlalchemy import (
    func,
    UUID,
    Text,
    Enum,
    String,
    Integer,
    Boolean,
    DateTime,
    TIMESTAMP,
)
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base
from campaigns.enums.campaign_enums import CampaignStatus


class CampaignModel(Base):

    __tablename__ = "campanias"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        name="id",
        unique=True,
        nullable=False,
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True, name="nombre_campania"
    )

    message: Mapped[str] = mapped_column(Text, nullable=False, name="mensaje")

    subject: Mapped[str | None] = mapped_column(String(255), nullable=True, name="asunto")

    channel: Mapped[str] = mapped_column(String(25), nullable=False, name="canal", default="auto")

    description: Mapped[str | None] = mapped_column(String(255), nullable=True, name="descripcion_campania")

    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus),
        nullable=False,
        default=CampaignStatus.SCHEDULED,
        name="estado_campania",
    )

    total_recipients: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, name="total_destinatarios"
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, name="programado_para")

    timezone: Mapped[str | None] = mapped_column(String(50), default="UTC", name="zona_horaria")

    fallback: Mapped[bool | None] = mapped_column(Boolean, default=True, name="fallback")

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        name="fecha_creacion",
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        onupdate=func.now(),
        name="fecha_actualizacion",
    )
