import uuid
from sqlalchemy import Column, String, Boolean, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP

from database.database import Base


class ContactModel(Base):

    __tablename__ = "contactos"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        name="id",
        default=uuid.uuid4,
    )

    email = Column(
        String, unique=True, index=True, name="correo_electronico", nullable=True
    )

    phone_number = Column(
        String, unique=True, index=True, name="numero_telefono", nullable=True
    )

    whatsapp_available = Column(Boolean, name="whatsapp_disponible", default=False)

    rcs_available = Column(Boolean, name="rcs_disponible", default=False)

    sms_available = Column(Boolean, name="sms_disponible", default=True)

    unsubscribed = Column(Boolean, name="desuscrito", default=False)

    extra_info = Column(JSONB, index=True, name="informacion_adicional", nullable=True)

    created_at = Column(
        TIMESTAMP, name="fecha_creacion", nullable=False, server_default=func.now()
    )

    updated_at = Column(
        TIMESTAMP, name="fecha_actualizacion", nullable=True, onupdate=func.now()
    )
