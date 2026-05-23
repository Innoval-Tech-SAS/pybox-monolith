import uuid

from sqlalchemy import CheckConstraint, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, validates

from base.audit_model import AuditModel
from users.enums.user_enums import UserRole, UserScope, VALID_ROLE_SCOPE

_CHECK_SQL = " OR ".join(
    f"(rol = '{r.value}' AND alcance = '{s.value}')"
    for r, s in VALID_ROLE_SCOPE
)


class RoleAssignmentModel(AuditModel):
    __tablename__ = "roles_asignados"
    __table_args__ = (
        UniqueConstraint(
            "id_usuario",
            "rol",
            "id_organizacion",
            name="uq_rol_usuario_org",
        ),
        CheckConstraint(_CHECK_SQL, name="ck_rol_alcance_valido"),
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

    @validates("role", "scope")
    def validate_role_scope(self, key: str, value: UserRole | UserScope) -> UserRole | UserScope:
        role = value if key == "role" else self.role
        scope = value if key == "scope" else self.scope
        if role is not None and scope is not None and (role, scope) not in VALID_ROLE_SCOPE:
            raise ValueError(f"Combinación inválida: {role} + {scope}")
        return value
