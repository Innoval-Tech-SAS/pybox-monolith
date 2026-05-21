from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from database.database import Base


class OrganizationModel(Base):
    __tablename__ = "entidades"

    id = Column(Integer, primary_key=True, autoincrement=True, name="id")
    name = Column(String(255), nullable=False, name="nombre")
    description = Column(String(255), nullable=True, name="descripcion")
    created_at = Column(DateTime, name="fecha_creacion", default=func.now())
    updated_at = Column(DateTime, nullable=True, name="fecha_actualizacion", onupdate=func.now())
    memberships = relationship(
        "OrganizationMembershipModel",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
