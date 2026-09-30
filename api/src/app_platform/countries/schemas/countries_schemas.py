"""Schemas de catálogo de países y tipos de documento."""

from pydantic import Field

from core.base.schema_base import BaseSchema


class DocumentTypeOption(BaseSchema):
    value: str = Field(description="Código del tipo de documento")
    label: str = Field(
        description="Etiqueta para mostrar (p. ej. 'CC – Cédula de Ciudadanía')"
    )


class DocumentTypeGroup(BaseSchema):
    group: str = Field(description="Encabezado del grupo (país o 'Universal')")
    options: list[DocumentTypeOption] = Field(description="Opciones del grupo")


class DocumentTypesResponse(BaseSchema):
    labels: dict[str, str] = Field(
        description=(
            "Mapa código → etiqueta legible (reemplaza el dict estático del front)"
        )
    )
    groups: list[DocumentTypeGroup] = Field(
        description="Tipos de documento de persona agrupados por país, para selects"
    )


class NationalityOption(BaseSchema):
    code: str = Field(description="Código ISO del país (CO, MX, AR, etc.)")
    name: str = Field(description="Nombre del país")
    flag_url: str = Field(description="URL de la bandera del país")
    phone_prefix: str = Field(
        description="Prefijo telefónico internacional (+57, +52, etc.)"
    )
    document_types: list[str] = Field(
        description="Tipos de documento de persona válidos para este país"
    )
    timezone: str = Field(description="Zona horaria IANA del país (ej. America/Bogota)")
    currency_code: str = Field(
        default="", description="Código ISO de la moneda (COP, MXN, etc.)"
    )
    fiscal_document_types: list[str] = Field(
        default_factory=list,
        description="Tipos de documento fiscal de organización válidos para este país",
    )
    mercantile_document_types: list[str] = Field(
        default_factory=list,
        description=(
            "Tipos de documento mercantil de organización válidos para este país"
        ),
    )
