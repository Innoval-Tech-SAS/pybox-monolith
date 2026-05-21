from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM

from database.database import Base
from users.enums.user_enums import UserRole, UserScope


class RoleAssignmentModel(Base):
    __tablename__ = "roles_asignados"
    __table_args__ = (
        UniqueConstraint(
            "id_usuario", "rol", "id_organizacion",
            name="uq_rol_usuario_org",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, name="id")
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, name="id_usuario")
    role = Column(ENUM(UserRole), nullable=False, name="rol")
    scope = Column(ENUM(UserScope), nullable=False, name="alcance")
    organization_id = Column(Integer, ForeignKey("entidades.id"), nullable=True, name="id_organizacion")
