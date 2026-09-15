import uuid
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import BaseModel


class UserPreferencesModel(BaseModel):
    __tablename__ = "preferencias_usuario"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("usuarios.id"), unique=True, nullable=False, name="id_usuario"
    )
    dismissed_tours: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list, name="tours_ignorados"
    )
