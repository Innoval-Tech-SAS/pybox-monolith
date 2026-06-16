import uuid

from sqlalchemy import SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel


class ChatModel(AuditModel):
    __tablename__ = "chats"
    __table_args__ = (UniqueConstraint("clave_dm", name="uq_chats_clave_dm"),)

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, name="id", default=uuid.uuid4
    )
    type: Mapped[int] = mapped_column(SmallInteger, nullable=False, name="tipo")
    dm_key: Mapped[str | None] = mapped_column(
        String(100), nullable=True, name="clave_dm", unique=True
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True, name="titulo")

    @staticmethod
    def build_dm_key(a: uuid.UUID, b: uuid.UUID) -> str:
        ids = sorted([str(a), str(b)])
        return f"{ids[0]}:{ids[1]}"
