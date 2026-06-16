import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel
from messaging.contacts.enums.contact_enums import ContactStatus


class ContactModel(AuditModel):

    __tablename__ = "contactos"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id_contacto"
    )

    content: Mapped[str] = mapped_column(Text, nullable=False, name="contenido")

    recipient: Mapped[str] = mapped_column(String(255), nullable=False, name="destinatario")

    status: Mapped[ContactStatus] = mapped_column(
        Enum(ContactStatus), nullable=False, default=ContactStatus.PENDING, name="estado"
    )

    debtor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("deudores.id"), nullable=True, index=True, name="id_deudor"
    )

    debtor_document: Mapped[str | None] = mapped_column(
        String(50), nullable=True, name="documento_deudor"
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, name="enviado_en"
    )

    provider_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, name="id_proveedor"
    )

    error: Mapped[str | None] = mapped_column(Text, nullable=True, name="error")

    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("campanias.id"), nullable=True, name="id_campania"
    )

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("entidades.id"), nullable=True, name="id_organizacion"
    )

    portfolio_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), nullable=True, name="id_portafolio"
    )

    snapshot_channel_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, name="snapshot_canal_id"
    )

    snapshot_currency: Mapped[str | None] = mapped_column(
        String(10), nullable=True, name="snapshot_moneda"
    )

    snapshot_unit_price: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=14, scale=6), nullable=True, name="snapshot_precio_unitario"
    )
