from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database.database import Base


class MessageStatusModel(Base):
    __tablename__ = "estados_mensaje"

    message_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("mensajes_chat.id", ondelete="CASCADE"),
        primary_key=True,
        name="message_id",
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        primary_key=True,
        name="user_id",
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, name="entregado_en"
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, name="leido_en"
    )
