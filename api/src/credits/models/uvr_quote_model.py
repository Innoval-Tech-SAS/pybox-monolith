from datetime import datetime

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from base.audit_model import AuditModel


class UVRQuoteModel(AuditModel):
    __tablename__ = "cotizaciones_uvr"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, name="id")
    quote_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, name="fecha_cotizacion"
    )
    quote_value: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False, name="valor_cotizacion")
    credit_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("creditos.id"), nullable=True, name="id_credito"
    )
