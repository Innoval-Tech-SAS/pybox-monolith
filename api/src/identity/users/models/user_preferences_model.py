import uuid
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel


class UserPreferencesModel(AuditModel):
    __tablename__ = "preferencias_usuario"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("usuarios.id"), unique=True, nullable=False, name="id_usuario"
    )
    dismissed_tours: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list, name="tours_ignorados"
    )
