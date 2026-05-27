from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class ChatMemberModel(Base):
    __tablename__ = "chat_members"

    chat_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("chats.id", ondelete="CASCADE"),
        primary_key=True,
        name="chat_id",
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        primary_key=True,
        name="user_id",
    )
    role: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, name="rol")
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), name="fecha_union"
    )
    left_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, name="fecha_salida"
    )
