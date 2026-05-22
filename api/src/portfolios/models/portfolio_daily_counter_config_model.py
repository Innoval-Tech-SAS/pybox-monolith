from datetime import date, datetime

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from base.audit_model import AuditModel


class PortfolioDailyCounterConfigModel(AuditModel):
    __tablename__ = "config_actualizacion_diaria_portafolio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, name="id")
    portfolio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("portafolios.id"), nullable=False, unique=True, index=True, name="id_portafolio"
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, name="habilitado")
    reactivation_mode: Mapped[str] = mapped_column(
        String, nullable=False, default="FROM_TODAY", name="modo_reactivacion"
    )
    updated_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=True, name="actualizado_por"
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, name="ultima_sincronizacion_at"
    )
    last_synced_cutoff_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, name="ultima_fecha_corte_sincronizada"
    )
