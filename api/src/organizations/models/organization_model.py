import uuid
from sqlalchemy import (
    func,
    UUID,
    Column,
    String,
    DateTime,
)
from sqlalchemy.orm import relationship


from database.database import Base


class OrganizationModel(Base):
    __tablename__ = "entidades"

    id = Column(UUID(as_uuid=True), primary_key=True, name="id", default=uuid.uuid4)
    name = Column(String(255), nullable=False, name="nombre")
    description = Column(String(255), nullable=True, name="descripcion")
    created_at = Column(DateTime, name="fecha_creacion", default=func.now())
    updated_at = Column(
        DateTime, nullable=True, name="fecha_actualizacion", onupdate=func.now()
    )
    memberships = relationship(
        "OrganizationMembershipModel",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
