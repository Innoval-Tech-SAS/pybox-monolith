import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, INTEGER, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel


class CampaignTimeModel(AuditModel):

    __tablename__ = "programacion_campanias"
    __table_args__ = (
        UniqueConstraint("id_campania", "hora_de_envio", "es_inmediato", name="uq_campaign_time"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id"
    )

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("campanias.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        name="id_campania",
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), nullable=False, index=True, name="id_organizacion"
    )

    next_execution: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True, name="siguiente_ejecucion"
    )

    timezone_iana: Mapped[str | None] = mapped_column(
        String(100), nullable=True, name="zona_horaria"
    )

    days_of_week: Mapped[list[int] | None] = mapped_column(
        ARRAY(INTEGER), nullable=True, name="dias_de_la_semana"
    )

    day_of_month: Mapped[int | None] = mapped_column(
        INTEGER, nullable=True, name="dia_del_mes"
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, name="esta_activo")

    is_immediate: Mapped[bool] = mapped_column(Boolean, default=False, name="es_inmediato")

    time_to_send: Mapped[str | None] = mapped_column(String(8), nullable=True, name="hora_de_envio")
