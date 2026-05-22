import uuid
from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base


class OrganizationMembershipModel(Base):
    __tablename__ = "membresias_organizacion"
    __table_args__ = (
        UniqueConstraint(
            "id_usuario", "id_entidad", name="uq_membresia_usuario_entidad"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, name="id")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False, name="id_usuario"
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("entidades.id"), nullable=False, name="id_entidad"
    )
    created_at: Mapped[datetime | None] = mapped_column(DateTime, name="fecha_creacion", default=func.now())
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), name="creado_por", nullable=False
    )

    user = relationship("UserModel", foreign_keys=[user_id], back_populates="memberships")
    organization = relationship("OrganizationModel", back_populates="memberships")
    creator = relationship("UserModel", foreign_keys=[created_by], back_populates="created_memberships")
