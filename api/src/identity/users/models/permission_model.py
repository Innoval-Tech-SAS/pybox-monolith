from sqlalchemy import Boolean, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel


class PermissionModel(AuditModel):
    __tablename__ = "permisos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, name="id")
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, name="nombre")
    label: Mapped[str | None] = mapped_column(String(255), nullable=True, name="etiqueta")
    description: Mapped[str | None] = mapped_column(String(500), nullable=True, name="descripcion")
    max_level_access: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, name="nivel_acceso_maximo")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, name="activo")
