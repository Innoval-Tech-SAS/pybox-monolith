"""Schemas de documentos y sus categorías por dominio."""

import uuid
from datetime import datetime

from pydantic import Field

from core.base.schema_base import BaseSchema


class DocumentCategoryOption(BaseSchema):
    """Opción de categoría para los selects del front.

    La forma es transversal; el catálogo ya no: cada dominio expone el suyo desde su
    propio controller (el enum único `DocumentCategory` desapareció junto con la
    asociación polimórfica).
    """

    value: str = Field(
        description="Código de la categoría (identidad, comprobante_pago, …)"
    )
    label: str = Field(
        description="Etiqueta para mostrar (p. ej. 'Documento de identidad')"
    )


class DocumentResponse(BaseSchema):
    """Metadatos de un documento: solo lo que describe al ARCHIVO.

    Deliberadamente sin la clave del objeto (el cliente descarga por id, nunca por ruta)
    y sin ámbito ni categoría: eso lo aporta la tabla de unión de cada dominio, que
    extiende este schema si necesita exponer su propia categoría.
    """

    id: uuid.UUID = Field(description="ID del documento")
    original_name: str = Field(description="Nombre con el que se subió el archivo")
    content_type: str = Field(description="Tipo MIME")
    size_bytes: int = Field(description="Tamaño en bytes")
    checksum: str = Field(
        description="SHA-256 del contenido, para verificar integridad"
    )
    created_at: datetime = Field(description="Fecha de subida")


class DocumentListResponse(BaseSchema):
    """Listado de documentos de un dueño."""

    items: list[DocumentResponse] = Field(
        description="Documentos, del más reciente al más antiguo"
    )
    total: int = Field(description="Cantidad de documentos")
