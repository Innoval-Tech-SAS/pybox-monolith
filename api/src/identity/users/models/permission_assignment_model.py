import uuid

from sqlalchemy import Boolean, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel
from identity.users.enums.user_enums import PermissionEffect, UserScope


class PermissionAssignmentModel(AuditModel):
    __tablename__ = "permisos_asignados"
    __table_args__ = (
        UniqueConstraint(
            "id_usuario", "id_permiso", "alcance", "id_organizacion",
            name="uq_permiso_usuario_scope",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False, name="id_usuario")
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey("permisos.id"), nullable=False, name="id_permiso")
    scope: Mapped[UserScope] = mapped_column(ENUM(UserScope), nullable=False, name="alcance")
    organization_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("entidades.id"), nullable=True, name="id_organizacion")
    effect: Mapped[PermissionEffect] = mapped_column(ENUM(PermissionEffect), nullable=False, default=PermissionEffect.GRANT, name="efecto")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, name="activo")
