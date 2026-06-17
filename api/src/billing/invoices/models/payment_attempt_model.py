import uuid
from typing import Any

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base.audit_model import AuditModel
from billing.invoices.enums.invoice_enums import PaymentAttemptStatus


class PaymentAttemptModel(AuditModel):
    __tablename__ = "intentos_pago"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("facturas.id", ondelete="CASCADE"), nullable=False, index=True, name="factura_id"
    )

    # Los intentos nunca se sobrescriben; siempre se crea un nuevo registro.
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1, name="numero_intento")

    # INV-{shortId}-{attemptNumber}-{timestamp} <= 60 caracteres
    bold_reference: Mapped[str | None] = mapped_column(
        String(60), nullable=True, index=True, name="referencia_bold"
    )
    bold_link_id: Mapped[str | None] = mapped_column(String, nullable=True, name="id_enlace_bold")
    payment_url: Mapped[str | None] = mapped_column(Text, nullable=True, name="url_pago")
    status: Mapped[PaymentAttemptStatus] = mapped_column(
        ENUM(PaymentAttemptStatus), nullable=False, default=PaymentAttemptStatus.ACTIVE, name="estado"
    )
    bold_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True, name="payload_bold")

    invoice = relationship("InvoiceModel", back_populates="attempts")
