import uuid
from datetime import datetime
from enum import Enum

from base.schema_base import BaseSchema
from countries.enums.country_enums import (
    Nationality,
    OrgFiscalDocumentType,
    OrgMercantileDocumentType,
    UserDocumentType,
)


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
