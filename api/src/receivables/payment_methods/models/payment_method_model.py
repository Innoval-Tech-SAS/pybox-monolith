import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import BaseModel
from receivables.payment_methods.enums.payment_method_enums import PaymentMethodType


class PaymentMethodModel(BaseModel):
    __tablename__ = "metodos_pago"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("entidades.id"), nullable=False, index=True, name="id_organizacion"
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False, name="nombre")
    type: Mapped[PaymentMethodType] = mapped_column(
        ENUM(PaymentMethodType, name="tipo_metodo_pago", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        name="tipo",
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True, name="descripcion")
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True, name="instrucciones")
    bank_name: Mapped[str | None] = mapped_column(String(160), nullable=True, name="banco")
    account_type: Mapped[str | None] = mapped_column(String(80), nullable=True, name="tipo_cuenta")
    # Cifrado (AES-GCM, igual que deudores.numero_documento): el texto plano nunca toca
    # la tabla. Sin longitud fija porque el ciphertext base64 no cabe en el String(120)
    # original.
    account_number: Mapped[str | None] = mapped_column(String, nullable=True, name="numero_cuenta")
    payment_link: Mapped[str | None] = mapped_column(String(500), nullable=True, name="link_pago")
    qr_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True, name="url_imagen_qr")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, name="activo")
