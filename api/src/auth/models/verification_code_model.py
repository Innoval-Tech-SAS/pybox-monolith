import uuid
from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base
from auth.enums.notification_enums import VerificationChannel


class VerificationCodeModel(Base):
    __tablename__ = "codigos_verificacion"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        name="id",
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        name="id_usuario",
    )
    channel: Mapped[VerificationChannel] = mapped_column(ENUM(VerificationChannel), nullable=False, name="canal")
    code: Mapped[str] = mapped_column(String(6), nullable=False, index=True, name="codigo")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, name="expira_en")
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, name="consumido_en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now(), name="creado_en")
