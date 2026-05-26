import uuid
from datetime import datetime
from enum import Enum

from pydantic import field_validator

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
    name: str
    description: str | None = None
    country: Nationality | None = None
    fiscal_document_type: OrgFiscalDocumentType | None = None
    fiscal_document_number: str | None = None
    mercantile_document_type: OrgMercantileDocumentType | None = None


class OrganizationUpdate(BaseSchema):
    name: str | None = None
    description: str | None = None
    country: Nationality | None = None
    fiscal_document_type: OrgFiscalDocumentType | None = None
    fiscal_document_number: str | None = None
    mercantile_document_type: OrgMercantileDocumentType | None = None


class OrganizationResponse(BaseSchema):
    id: uuid.UUID
    name: str
    description: str | None = None
    country: Nationality | None = None
    fiscal_document_type: OrgFiscalDocumentType | None = None
    fiscal_document_number: str | None = None
    mercantile_document_type: OrgMercantileDocumentType | None = None
    created_at: datetime
    updated_at: datetime | None = None

    @field_validator("fiscal_document_number", mode="before")
    @classmethod
    def decrypt_fiscal(cls, v: str | None) -> str | None:
        return _safe_decrypt(v)


class OrgRegisterResponse(BaseSchema):
    id: uuid.UUID
    name: str
    description: str | None = None
    country: Nationality | None = None
    fiscal_document_type: OrgFiscalDocumentType | None = None
    fiscal_document_number: str | None = None
    mercantile_document_type: OrgMercantileDocumentType | None = None
    representative_document_file: str | None = None
    created_at: datetime

    @field_validator("fiscal_document_number", mode="before")
    @classmethod
    def decrypt_fiscal(cls, v: str | None) -> str | None:
        return _safe_decrypt(v)
