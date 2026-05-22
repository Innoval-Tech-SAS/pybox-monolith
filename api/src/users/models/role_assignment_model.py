import uuid

from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from base.audit_model import AuditModel
from users.enums.user_enums import UserRole, UserScope


class RoleAssignmentModel(AuditModel):
    __tablename__ = "roles_asignados"
    __table_args__ = (
        UniqueConstraint(
            "id_usuario",
            "rol",
            "id_organizacion",
            name="uq_rol_usuario_org",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False, name="id_usuario"
    )
    role: Mapped[UserRole] = mapped_column(ENUM(UserRole), nullable=False, name="rol")
    scope: Mapped[UserScope] = mapped_column(
        ENUM(UserScope), nullable=False, name="alcance"
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("entidades.id"),
        nullable=True,
        name="id_organizacion",
    )
