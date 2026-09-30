"""Schemas de organizaciones: alta, edición, verificación y documentos."""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import Field, computed_field

from core.base.schema_base import BaseSchema
from identity.organizations.enums.organization_enums import EntitySectors


class RepresentativeMode(str, Enum):
    SELF = "self"
    SELECT = "select"
    CREATE = "create"


class EntitySectorOption(BaseSchema):
    """Opción de sector para los selects del front, que no mantiene su propia lista."""

    value: str = Field(description="Código del sector (entidad_financiera, fintech, …)")
    label: str = Field(
        description="Etiqueta para mostrar (p. ej. 'Entidad financiera')"
    )


class OrganizationCreate(BaseSchema):
    name: str = Field(description="Nombre de la organización")
    sector: EntitySectors = Field(description="Sector al que pertenece la entidad")
    description: str | None = Field(default=None, description="Descripción opcional")
    country: str | None = Field(default=None, description="País de la organización")
    fiscal_document_type: str | None = Field(
        default=None, description="Tipo de documento fiscal"
    )
    fiscal_document_number: str | None = Field(
        default=None, description="Número de documento fiscal"
    )
    mercantile_document_type: str | None = Field(
        default=None, description="Tipo de documento mercantil"
    )


class OrganizationUpdate(BaseSchema):
    name: str | None = Field(default=None, description="Nombre de la organización")
    sector: EntitySectors | None = Field(
        default=None, description="Sector al que pertenece la entidad"
    )
    description: str | None = Field(default=None, description="Descripción")
    country: str | None = Field(default=None, description="País")
    fiscal_document_type: str | None = Field(
        default=None, description="Tipo de documento fiscal"
    )
    fiscal_document_number: str | None = Field(
        default=None, description="Número de documento fiscal"
    )
    mercantile_document_type: str | None = Field(
        default=None, description="Tipo de documento mercantil"
    )


class OrganizationResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID único de la organización")
    name: str = Field(description="Nombre")
    sector: EntitySectors = Field(description="Sector al que pertenece la entidad")
    description: str | None = Field(default=None, description="Descripción")
    country: str | None = Field(default=None, description="País")
    fiscal_document_type: str | None = Field(
        default=None, description="Tipo de documento fiscal"
    )
    fiscal_document_number: str | None = Field(
        default=None, description="Número de documento fiscal"
    )
    fiscal_document_id: uuid.UUID | None = Field(default=None, exclude=True)
    mercantile_document_type: str | None = Field(
        default=None, description="Tipo de documento mercantil"
    )
    mercantile_document_id: uuid.UUID | None = Field(default=None, exclude=True)
    representative_document_id: uuid.UUID | None = Field(default=None, exclude=True)
    logo_document_id: uuid.UUID | None = Field(default=None, exclude=True)
    verification_status: str | None = Field(
        default=None, description="Estado de verificación"
    )
    created_at: datetime = Field(description="Fecha de creación")
    updated_at: datetime | None = Field(
        default=None, description="Fecha de última actualización"
    )

    def _document_url(self, document_id: uuid.UUID | None) -> str | None:
        if document_id is None:
            return None
        return f"/organizations/{self.id}/documents/{document_id}/content"

    @computed_field(description="URL del documento fiscal")  # type: ignore[misc]
    @property
    def fiscal_document_file(self) -> str | None:
        return self._document_url(self.fiscal_document_id)

    @computed_field(description="URL del documento mercantil")  # type: ignore[misc]
    @property
    def mercantile_document_file(self) -> str | None:
        return self._document_url(self.mercantile_document_id)

    @computed_field(  # type: ignore[misc]
        description="URL del documento del representante"
    )
    @property
    def representative_document_file(self) -> str | None:
        return self._document_url(self.representative_document_id)

    @computed_field(description="URL del logo de la organización")  # type: ignore[misc]
    @property
    def logo_url(self) -> str | None:
        return self._document_url(self.logo_document_id)


class OrgRegisterResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID de la organización creada")
    name: str = Field(description="Nombre")
    sector: EntitySectors = Field(description="Sector al que pertenece la entidad")
    description: str | None = Field(default=None, description="Descripción")
    country: str | None = Field(default=None, description="País")
    fiscal_document_type: str | None = Field(
        default=None, description="Tipo de documento fiscal"
    )
    fiscal_document_number: str | None = Field(
        default=None, description="Número de documento fiscal"
    )
    mercantile_document_type: str | None = Field(
        default=None, description="Tipo de documento mercantil"
    )
    representative_document_id: uuid.UUID | None = Field(default=None, exclude=True)
    created_at: datetime = Field(description="Fecha de creación")

    @computed_field(  # type: ignore[misc]
        description="URL del documento del representante"
    )
    @property
    def representative_document_file(self) -> str | None:
        if self.representative_document_id is None or self.id is None:
            return None
        return (
            f"/organizations/{self.id}/documents/"
            f"{self.representative_document_id}/content"
        )
