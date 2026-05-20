import uuid
from sqlalchemy import (
    func,
    UUID,
    Column,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from organizations.models.organization_model import OrganizationModel
from users.enums.user_enums import UserRole, UserScope
from database.database import Base


class OrganizationMembershipModel(Base):
    __tablename__ = "membresias_organizacion"
    __table_args__ = (
        UniqueConstraint(
            "id_usuario",
            "id_entidad",
            name="uq_membresia_usuario_entidad",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, name="id", default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False,
        name="id_usuario",
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("entidades.id"),
        nullable=False,
        name="id_entidad",
    )
    role = Column(
        ENUM(UserRole),
        nullable=False,
        default=UserRole.USER_ORGANIZATION,
        name="rol",
    )
    scope = Column(
        ENUM(UserScope),
        nullable=False,
        default=UserScope.ORGANIZATION,
        name="alcance",
    )
    created_at = Column(DateTime, name="fecha_creacion", default=func.now())
    updated_at = Column(
        DateTime,
        nullable=True,
        name="fecha_actualizacion",
        onupdate=func.now(),
    )

    user = relationship("UserModel", back_populates="memberships")
    organization = relationship("OrganizationModel", back_populates="memberships")
