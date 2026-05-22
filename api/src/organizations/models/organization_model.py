import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import ENUM, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from countries.enums.country_enums import (
    Nationality,
    OrgFiscalDocumentType,
    OrgMercantileDocumentType,
)


class OrganizationModel(Base):
    __tablename__ = "entidades"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        name="id",
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, name="nombre")
    description: Mapped[str | None] = mapped_column(String(255), nullable=True, name="descripcion")
    country: Mapped[Nationality | None] = mapped_column(ENUM(Nationality), nullable=True, name="pais")

    fiscal_document_type: Mapped[OrgFiscalDocumentType | None] = mapped_column(
        ENUM(OrgFiscalDocumentType), nullable=True, name="tipo_documento_fiscal"
    )
    fiscal_document_number: Mapped[str | None] = mapped_column(
        String(50), nullable=True, name="numero_documento_fiscal"
    )
    fiscal_document_file: Mapped[str | None] = mapped_column(
        String(500), nullable=True, name="archivo_documento_fiscal"
    )

    mercantile_document_type: Mapped[OrgMercantileDocumentType | None] = mapped_column(
        ENUM(OrgMercantileDocumentType), nullable=True, name="tipo_documento_mercantil"
    )
    mercantile_document_file: Mapped[str | None] = mapped_column(
        String(500), nullable=True, name="archivo_documento_mercantil"
    )

    created_at: Mapped[datetime | None] = mapped_column(DateTime, name="fecha_creacion", default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, name="fecha_actualizacion", onupdate=func.now()
    )

    memberships = relationship(
        "OrganizationMembershipModel",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
