from datetime import datetime

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel


class CreditAdjustmentModel(AuditModel):
    __tablename__ = "ajustes_credito"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, name="id")
    credit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("creditos.id"), nullable=False, index=True, name="id_credito"
    )
    adjustment_type: Mapped[str] = mapped_column(String, nullable=False, name="tipo_ajuste")
    adjustment_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, name="monto_ajuste")
    applied_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, name="fecha_aplicacion")
    note: Mapped[str | None] = mapped_column(String, nullable=True, name="nota")
