import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ENUM, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base.audit_model import AuditModel
from app_platform.countries.enums.country_enums import (
    Nationality,
    OrgFiscalDocumentType,
    OrgMercantileDocumentType,
)
from identity.organizations.enums.organization_enums import VerificationStatus


class OrganizationModel(AuditModel):
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
        String(255), nullable=True, name="numero_documento_fiscal"
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
    representative_document_file: Mapped[str | None] = mapped_column(
        String(500), nullable=True, name="archivo_documento_representante"
    )
    verification_status: Mapped[VerificationStatus] = mapped_column(
        ENUM(VerificationStatus), nullable=False, default=VerificationStatus.PENDING, name="estado_verificacion"
    )

    memberships = relationship(
        "OrganizationMembershipModel",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
