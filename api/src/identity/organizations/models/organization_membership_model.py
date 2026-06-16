import uuid

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base.audit_model import AuditModel


class OrganizationMembershipModel(AuditModel):
    __tablename__ = "membresias_organizacion"
    __table_args__ = (
        UniqueConstraint(
            "id_usuario", "id_entidad", name="uq_membresia_usuario_entidad"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, name="id_usuario"
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("entidades.id"), nullable=False, name="id_entidad"
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("usuarios.id"), name="creado_por", nullable=False
    )
    is_legal_representative: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, name="es_representante_legal"
    )

    user = relationship("UserModel", foreign_keys=[user_id], back_populates="memberships")
    organization = relationship("OrganizationModel", back_populates="memberships")
    creator = relationship("UserModel", foreign_keys=[created_by], back_populates="created_memberships")
