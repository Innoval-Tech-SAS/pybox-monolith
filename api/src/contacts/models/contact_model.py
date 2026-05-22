import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class ContactModel(Base):

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

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, name="fecha_creacion", nullable=False, server_default=func.now()
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, name="fecha_actualizacion", nullable=True, onupdate=func.now()
    )
