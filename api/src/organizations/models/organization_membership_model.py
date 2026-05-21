from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship

from database.database import Base


class OrganizationMembershipModel(Base):
    __tablename__ = "membresias_organizacion"
    __table_args__ = (
        UniqueConstraint(
            "id_usuario", "id_entidad", name="uq_membresia_usuario_entidad"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, name="id")
    user_id = Column(
        Integer, ForeignKey("usuarios.id"), nullable=False, name="id_usuario"
    )
    organization_id = Column(
        Integer, ForeignKey("entidades.id"), nullable=False, name="id_entidad"
    )
    created_at = Column(DateTime, name="fecha_creacion", default=func.now())
    created_by = Column(
        Integer, ForeignKey("usuarios.id"), name="creado_por", nullable=False
    )

    user = relationship("UserModel", foreign_keys=[user_id], back_populates="memberships")
    organization = relationship("OrganizationModel", back_populates="memberships")
    creator = relationship("UserModel", foreign_keys=[created_by], back_populates="created_memberships")
