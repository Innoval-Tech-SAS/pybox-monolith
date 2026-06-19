import uuid
from datetime import datetime

from sqlalchemy import ARRAY, Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel
from messaging.campaigns.enums.campaign_enums import CampaignStatus, Periodicity


class CampaignModel(AuditModel):

    __tablename__ = "campanias"

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
        String(255), nullable=False, index=True, name="nombre_campania"
    )

    message: Mapped[str] = mapped_column(Text, nullable=False, name="mensaje")

    subject: Mapped[str | None] = mapped_column(String(255), nullable=True, name="asunto")

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("canales.id_canal"), nullable=False, name="id_canal"
    )

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

    segment_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("segmentos.id"), nullable=True, index=True, name="id_segmento"
    )

    template_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("plantillas.id"), nullable=True, name="id_plantilla"
    )

    periodicity: Mapped[Periodicity | None] = mapped_column(
        Enum(Periodicity), nullable=True, name="periodicidad"
    )

    time_to_send: Mapped[str | None] = mapped_column(
        String(8), nullable=True, name="hora_de_envio"
    )

    is_immediate: Mapped[bool] = mapped_column(Boolean, default=False, name="es_inmediato")

    days_of_week: Mapped[list[int] | None] = mapped_column(
        ARRAY(Integer), nullable=True, name="dias_semana"
    )
