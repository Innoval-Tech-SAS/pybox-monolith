from sqlalchemy import Boolean, Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM

from database.database import Base
from users.enums.user_enums import PermissionEffect, UserScope


class PermissionAssignmentModel(Base):
    __tablename__ = "permisos_asignados"
    __table_args__ = (
        UniqueConstraint(
            "id_usuario", "id_permiso", "alcance", "id_organizacion",
            name="uq_permiso_usuario_scope",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, name="id")
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, name="id_usuario")
    permission_id = Column(Integer, ForeignKey("permisos.id"), nullable=False, name="id_permiso")
    scope = Column(ENUM(UserScope), nullable=False, name="alcance")
    organization_id = Column(Integer, ForeignKey("entidades.id"), nullable=True, name="id_organizacion")
    effect = Column(ENUM(PermissionEffect), nullable=False, default=PermissionEffect.GRANT, name="efecto")
    is_active = Column(Boolean, nullable=False, default=True, name="activo")
