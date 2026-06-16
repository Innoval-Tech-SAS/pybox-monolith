import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel


class CampaignResultModel(AuditModel):

    __tablename__ = "resultados_campanias"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id"
    )

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("campanias.id"),
        nullable=False,
        index=True,
        name="id_campania",
    )

    campaign_time_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("programacion_campanias.id", ondelete="SET NULL"),
        nullable=True,
        name="id_programacion",
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), nullable=False, index=True, name="id_organizacion"
    )

    total_sent: Mapped[int] = mapped_column(Integer, default=0, name="total_enviados")

    success_count: Mapped[int] = mapped_column(Integer, default=0, name="exitosos")

    failure_count: Mapped[int] = mapped_column(Integer, default=0, name="con_errores")

    unique_customers: Mapped[int] = mapped_column(Integer, default=0, name="clientes_unicos")

    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), name="fecha_envio"
    )
