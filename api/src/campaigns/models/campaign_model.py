import uuid
from sqlalchemy import (
    func,
    UUID,
    Text,
    Enum,
    String,
    Integer,
    Column,
    Boolean,
    DateTime,
    TIMESTAMP,
)

from database.database import Base
from campaigns.enums.campaign_enums import CampaignStatus


class CampaignModel(Base):

    __tablename__ = "campanias"

    id = Column(
        UUID(as_uuid=True),
        name="id",
        unique=True,
        nullable=False,
        primary_key=True,
        default=uuid.uuid4,
    )

    name = Column(
        String(255), nullable=False, unique=True, index=True, name="nombre_campania"
    )

    message = Column(Text, nullable=False, name="mensaje")

    subject = Column(String(255), nullable=True, name="asunto")

    channel = Column(String(25), nullable=False, name="canal", default="auto")

    description = Column(String(255), nullable=True, name="descripcion_campania")

    status = Column(
        Enum(CampaignStatus),
        nullable=False,
        default=CampaignStatus.SCHEDULED,
        name="estado_campania",
    )

    total_recipients = Column(
        Integer, nullable=False, default=0, name="total_destinatarios"
    )

    scheduled_at = Column(DateTime, nullable=True, name="programado_para")

    timezone = Column(String(50), default="UTC", name="zona_horaria")

    fallback = Column(Boolean, default=True, name="fallback")

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        name="fecha_creacion",
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        onupdate=func.now(),
        name="fecha_actualizacion",
    )
