import uuid

from sqlalchemy import SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from base.audit_model import AuditModel


class ChatModel(AuditModel):
    __tablename__ = "chats"
    __table_args__ = (UniqueConstraint("clave_dm", name="uq_chats_clave_dm"),)

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, name="id", default=lambda: str(uuid.uuid4())
    )
    type: Mapped[int] = mapped_column(SmallInteger, nullable=False, name="tipo")
    dm_key: Mapped[str | None] = mapped_column(
        String(100), nullable=True, name="clave_dm", unique=True
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True, name="titulo")

    @staticmethod
    def build_dm_key(a: int, b: int) -> str:
        return f"{min(a, b)}:{max(a, b)}"
