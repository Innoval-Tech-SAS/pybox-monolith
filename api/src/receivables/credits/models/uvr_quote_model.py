import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from core.base.audit_model import AuditModel


class UVRQuoteModel(AuditModel):
    __tablename__ = "cotizaciones_uvr"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    quote_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, name="fecha_cotizacion"
    )
    quote_value: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False, name="valor_cotizacion")
    credit_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("creditos.id"), nullable=True, name="id_credito"
    )
