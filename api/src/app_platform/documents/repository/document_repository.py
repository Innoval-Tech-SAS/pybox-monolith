import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.documents.models.document_model import DocumentModel
from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase


class DocumentRepository(SoftDeleteRepositoryBase[DocumentModel]):
    """Acceso a la tabla base de metadatos de archivo.

    Es deliberadamente pobre: `documentos` ya no sabe de quién es cada fila, así que acá
    no hay ninguna consulta "por dueño". Ese filtro vive en el repository de cada tabla
    de unión (`DebtorDocumentRepository`, `TicketDocumentRepository`, …), que es el único
    que conoce la columna de dueño y puede hacer el JOIN.
    """

    model_class = DocumentModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    def _visible(self):
        return select(DocumentModel).where(DocumentModel.deleted_at.is_(None))

    async def get_by_organization(
        self, document_id: uuid.UUID, organization_id: uuid.UUID
    ) -> Optional[DocumentModel]:
        """El documento solo se ve si es de esa organización.

        Sirve a los casos 1:1 de la entidad (fiscal, mercantil, representante): ahí el
        documento no cuelga de ninguna tabla de unión, y `id_organizacion` es el único
        scope de tenant que tiene la fila.
        """
        return await self.session.scalar(
            self._visible().where(
                DocumentModel.id == document_id,
                DocumentModel.organization_id == organization_id,
            )
        )

    async def soft_delete_by_organization(self, organization_id: uuid.UUID, deleted_at: datetime) -> None:
        """Baja en cascada de los documentos de la organización con el sello de la organización."""
        await self.soft_delete_where(DocumentModel.organization_id == organization_id, deleted_at=deleted_at)

    async def restore_by_organization(self, organization_id: uuid.UUID, deleted_at: datetime) -> None:
        """Inverso de ``soft_delete_by_organization``: solo lo que cayó con la organización."""
        await self.restore_where(DocumentModel.organization_id == organization_id, deleted_at=deleted_at)
