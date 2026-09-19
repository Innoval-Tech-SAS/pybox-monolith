import uuid
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.documents.models.document_model import DocumentModel
from app_platform.support.enums.support_enums import TicketDocumentCategory
from app_platform.support.models.ticket_document_model import TicketDocumentModel
from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase

# Prefijo del dominio en la clave del objeto (`<dominio>/<dueno>/<uuid><ext>`).
# Lo aporta el dominio dueño del documento; reemplaza a `DocumentOwnerScope.TICKET`, que
# desapareció junto con la asociación polimórfica.
TICKET_DOCUMENT_STORAGE_DOMAIN = "ticket"


class TicketDocumentRepository(SoftDeleteRepositoryBase[TicketDocumentModel]):
    """Adjuntos de un ticket de soporte. Mismo criterio que `DebtorDocumentRepository`:
    el JOIN con `documentos` va en la query, no en un lazy load."""

    model_class = TicketDocumentModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    def _visible_join(self):
        return (
            select(TicketDocumentModel, DocumentModel)
            .join(DocumentModel, DocumentModel.id == TicketDocumentModel.document_id)
            .where(
                TicketDocumentModel.deleted_at.is_(None),
                DocumentModel.deleted_at.is_(None),
            )
        )

    async def list_by_ticket(
        self, ticket_id: uuid.UUID, category: Optional[TicketDocumentCategory] = None
    ) -> Sequence[tuple[TicketDocumentModel, DocumentModel]]:
        query = self._visible_join().where(TicketDocumentModel.ticket_id == ticket_id)
        if category is not None:
            query = query.where(TicketDocumentModel.category == category)
        result = await self.session.execute(query.order_by(DocumentModel.created_at.desc()))
        return [(link, document) for link, document in result.all()]

    async def get_owned(
        self, ticket_id: uuid.UUID, document_id: uuid.UUID
    ) -> Optional[tuple[TicketDocumentModel, DocumentModel]]:
        row = (
            await self.session.execute(
                self._visible_join().where(
                    TicketDocumentModel.ticket_id == ticket_id,
                    TicketDocumentModel.document_id == document_id,
                )
            )
        ).first()
        return (row[0], row[1]) if row is not None else None

    async def get_by_checksum(
        self, owner_id: uuid.UUID, checksum: str
    ) -> Optional[TicketDocumentModel]:
        return await self.session.scalar(
            select(TicketDocumentModel)
            .join(DocumentModel, DocumentModel.id == TicketDocumentModel.document_id)
            .where(
                TicketDocumentModel.ticket_id == owner_id,
                DocumentModel.checksum == checksum,
                TicketDocumentModel.deleted_at.is_(None),
            )
        )
