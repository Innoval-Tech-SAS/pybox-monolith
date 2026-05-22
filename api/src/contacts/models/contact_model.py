import uuid

from sqlalchemy import String, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from base.audit_model import AuditModel


class ContactModel(AuditModel):

    __tablename__ = "contactos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        name="id",
        default=uuid.uuid4,
    )

    email: Mapped[str | None] = mapped_column(
        String, unique=True, index=True, name="correo_electronico", nullable=True
    )

    phone_number: Mapped[str | None] = mapped_column(
        String, unique=True, index=True, name="numero_telefono", nullable=True
    )

    whatsapp_available: Mapped[bool | None] = mapped_column(Boolean, name="whatsapp_disponible", default=False)

    rcs_available: Mapped[bool | None] = mapped_column(Boolean, name="rcs_disponible", default=False)

    sms_available: Mapped[bool | None] = mapped_column(Boolean, name="sms_disponible", default=True)

    unsubscribed: Mapped[bool | None] = mapped_column(Boolean, name="desuscrito", default=False)

    extra_info: Mapped[dict | None] = mapped_column(JSONB, index=True, name="informacion_adicional", nullable=True)
