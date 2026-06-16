from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel


class UserPreferencesModel(AuditModel):
    __tablename__ = "preferencias_usuario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, name="id")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), unique=True, nullable=False, name="id_usuario"
    )
    dismissed_tours: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list, name="tours_ignorados"
    )
