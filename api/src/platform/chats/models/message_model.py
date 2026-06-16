import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel


class MessageModel(AuditModel):
    __tablename__ = "mensajes_chat"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, name="id", default=lambda: str(uuid.uuid4())
    )
    chat_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        name="chat_id",
        index=True,
    )
    sender_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False, name="remitente_id"
    )
    body: Mapped[str] = mapped_column(Text, nullable=False, name="cuerpo")
