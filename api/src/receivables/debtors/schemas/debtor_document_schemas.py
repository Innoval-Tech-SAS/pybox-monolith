"""Schema de un documento del repositorio documental de un deudor."""

from pydantic import Field

from app_platform.documents.schemas.document_schemas import DocumentResponse
from core.base.schema_base import BaseSchema
from receivables.debtors.enums.debtor_document_enums import DebtorDocumentCategory


class DebtorDocumentResponse(DocumentResponse):
    """Metadatos de archivo (heredados) + la categoría, que vive en `documentos_deudor`
    y no en `documentos`."""

    category: DebtorDocumentCategory = Field(
        description="Categoría del documento del deudor"
    )


class DebtorDocumentListResponse(BaseSchema):
    """Repositorio documental de un deudor."""

    items: list[DebtorDocumentResponse] = Field(
        description="Documentos, del más reciente al más antiguo"
    )
    total: int = Field(description="Cantidad de documentos")
