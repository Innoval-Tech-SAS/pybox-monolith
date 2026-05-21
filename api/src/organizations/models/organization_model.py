import uuid
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, UUID, func
from sqlalchemy.dialects.postgresql import ENUM

from database.database import Base
from countries.enums.country_enums import (
    Nationality,
    OrgFiscalDocumentType,
    OrgMercantileDocumentType,
)


class OrganizationModel(Base):
    __tablename__ = "entidades"

    id = Column(
        UUID(as_uuid=True),
        name="id",
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(255), nullable=False, name="nombre")
    description = Column(String(255), nullable=True, name="descripcion")
    country = Column(ENUM(Nationality), nullable=True, name="pais")

    fiscal_document_type = Column(
        ENUM(OrgFiscalDocumentType), nullable=True, name="tipo_documento_fiscal"
    )
    fiscal_document_number = Column(
        String(50), nullable=True, name="numero_documento_fiscal"
    )
    fiscal_document_file = Column(
        String(500), nullable=True, name="archivo_documento_fiscal"
    )

    mercantile_document_type = Column(
        ENUM(OrgMercantileDocumentType), nullable=True, name="tipo_documento_mercantil"
    )
    mercantile_document_file = Column(
        String(500), nullable=True, name="archivo_documento_mercantil"
    )

    created_at = Column(DateTime, name="fecha_creacion", default=func.now())
    updated_at = Column(
        DateTime, nullable=True, name="fecha_actualizacion", onupdate=func.now()
    )
    memberships = relationship(
        "OrganizationMembershipModel",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
