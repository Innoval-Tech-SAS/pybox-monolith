import uuid
from datetime import datetime
from enum import Enum

from pydantic import Field, field_validator

from base.schema_base import BaseSchema
from countries.enums.country_enums import (
    Nationality,
    OrgFiscalDocumentType,
    OrgMercantileDocumentType,
    UserDocumentType,
)
from security.services.encrypt_service import encrypt_service


def _safe_decrypt(value: str | None) -> str | None:
    if value is None:
        return None
    return encrypt_service.decrypt_to_str(value)


class RepresentativeMode(str, Enum):
    SELF = "self"
    SELECT = "select"
    CREATE = "create"


class OrganizationCreate(BaseSchema):
    name: str = Field(description="Nombre de la organización")
    description: str | None = Field(default=None, description="Descripción opcional")
    country: Nationality | None = Field(default=None, description="País de la organización")
    fiscal_document_type: OrgFiscalDocumentType | None = Field(default=None, description="Tipo de documento fiscal")
    fiscal_document_number: str | None = Field(default=None, description="Número de documento fiscal")
    mercantile_document_type: OrgMercantileDocumentType | None = Field(default=None, description="Tipo de documento mercantil")


class OrganizationUpdate(BaseSchema):
    name: str | None = Field(default=None, description="Nombre de la organización")
    description: str | None = Field(default=None, description="Descripción")
    country: Nationality | None = Field(default=None, description="País")
    fiscal_document_type: OrgFiscalDocumentType | None = Field(default=None, description="Tipo de documento fiscal")
    fiscal_document_number: str | None = Field(default=None, description="Número de documento fiscal")
    mercantile_document_type: OrgMercantileDocumentType | None = Field(default=None, description="Tipo de documento mercantil")


class OrganizationResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID único de la organización")
    name: str = Field(description="Nombre")
    description: str | None = Field(default=None, description="Descripción")
    country: Nationality | None = Field(default=None, description="País")
    fiscal_document_type: OrgFiscalDocumentType | None = Field(default=None, description="Tipo de documento fiscal")
    fiscal_document_number: str | None = Field(default=None, description="Número de documento fiscal")
    fiscal_document_file: str | None = Field(default=None, description="URL del documento fiscal")
    mercantile_document_type: OrgMercantileDocumentType | None = Field(default=None, description="Tipo de documento mercantil")
    mercantile_document_file: str | None = Field(default=None, description="URL del documento mercantil")
    representative_document_file: str | None = Field(default=None, description="URL del documento del representante")
    verification_status: str | None = Field(default=None, description="Estado de verificación")
    created_at: datetime = Field(description="Fecha de creación")
    updated_at: datetime | None = Field(default=None, description="Fecha de última actualización")

    @field_validator("fiscal_document_number", mode="before")
    @classmethod
    def decrypt_fiscal(cls, v: str | None) -> str | None:
        return _safe_decrypt(v)

    @field_validator("fiscal_document_file", "mercantile_document_file", "representative_document_file", mode="before")
    @classmethod
    def to_public_url(cls, v: str | None) -> str | None:
        if not v:
            return None
        if v.startswith("/files/"):
            return v
        return "/files/" + v.replace("\\", "/")


class OrgRegisterResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID de la organización creada")
    name: str = Field(description="Nombre")
    description: str | None = Field(default=None, description="Descripción")
    country: Nationality | None = Field(default=None, description="País")
    fiscal_document_type: OrgFiscalDocumentType | None = Field(default=None, description="Tipo de documento fiscal")
    fiscal_document_number: str | None = Field(default=None, description="Número de documento fiscal")
    mercantile_document_type: OrgMercantileDocumentType | None = Field(default=None, description="Tipo de documento mercantil")
    representative_document_file: str | None = Field(default=None, description="URL del documento del representante")
    created_at: datetime = Field(description="Fecha de creación")

    @field_validator("fiscal_document_number", mode="before")
    @classmethod
    def decrypt_fiscal(cls, v: str | None) -> str | None:
        return _safe_decrypt(v)
