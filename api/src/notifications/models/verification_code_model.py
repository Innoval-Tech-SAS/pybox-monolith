import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UUID, func
from sqlalchemy.dialects.postgresql import ENUM

from database.database import Base
from notifications.enums.notification_enums import VerificationChannel


class VerificationCodeModel(Base):
    __tablename__ = "codigos_verificacion"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        name="id",
    )
    user_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        name="id_usuario",
    )
    channel = Column(ENUM(VerificationChannel), nullable=False, name="canal")
    code = Column(String(6), nullable=False, index=True, name="codigo")
    expires_at = Column(DateTime, nullable=False, name="expira_en")
    consumed_at = Column(DateTime, nullable=True, name="consumido_en")
    created_at = Column(DateTime, nullable=False, default=func.now(), name="creado_en")
