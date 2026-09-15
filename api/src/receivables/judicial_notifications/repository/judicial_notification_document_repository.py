import uuid
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.documents.models.document_model import DocumentModel
from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.judicial_notifications.models.judicial_notification_document_model import (
    JudicialNotificationDocumentModel,
)

# Prefijo del dominio en la clave del objeto (`<dominio>/<dueno>/<uuid><ext>`).
# Lo aporta el dominio dueño del documento; reemplaza a
# `DocumentOwnerScope.JUDICIAL_NOTIFICATION`, que desapareció junto con la asociación
# polimórfica.
JUDICIAL_NOTIFICATION_DOCUMENT_STORAGE_DOMAIN = "notificacion_judicial"


class JudicialNotificationDocumentRepository(
    SoftDeleteRepositoryBase[JudicialNotificationDocumentModel]
):
    """Adjuntos de notificaciones judiciales. Mismo criterio que
    `DebtorDocumentRepository`: el JOIN con `documentos` va en la query, no en un lazy
    load. Sin filtro por categoría porque la tabla no tiene esa columna."""

    model_class = JudicialNotificationDocumentModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    def _visible_join(self):
        return (
            select(JudicialNotificationDocumentModel, DocumentModel)
            .join(
                DocumentModel,
                DocumentModel.id == JudicialNotificationDocumentModel.document_id,
            )
            .where(
                JudicialNotificationDocumentModel.deleted_at.is_(None),
                DocumentModel.deleted_at.is_(None),
            )
        )

    async def list_by_notification(
        self, notification_id: uuid.UUID
    ) -> Sequence[tuple[JudicialNotificationDocumentModel, DocumentModel]]:
        result = await self.session.execute(
            self._visible_join()
            .where(JudicialNotificationDocumentModel.judicial_notification_id == notification_id)
            .order_by(DocumentModel.created_at.desc())
        )
        return [(link, document) for link, document in result.all()]

    async def list_by_notifications(
        self, notification_ids: Sequence[uuid.UUID]
    ) -> Sequence[tuple[JudicialNotificationDocumentModel, DocumentModel]]:
        """Adjuntos de varias notificaciones en UNA sola query (`IN (...)`), para que
        listar el buzón no dispare una consulta por fila."""
        if not notification_ids:
            return []
        result = await self.session.execute(
            self._visible_join()
            .where(
                JudicialNotificationDocumentModel.judicial_notification_id.in_(notification_ids)
            )
            .order_by(DocumentModel.created_at.desc())
        )
        return [(link, document) for link, document in result.all()]

    async def get_owned(
        self, notification_id: uuid.UUID, document_id: uuid.UUID
    ) -> Optional[tuple[JudicialNotificationDocumentModel, DocumentModel]]:
        row = (
            await self.session.execute(
                self._visible_join().where(
                    JudicialNotificationDocumentModel.judicial_notification_id == notification_id,
                    JudicialNotificationDocumentModel.document_id == document_id,
                )
            )
        ).first()
        return (row[0], row[1]) if row is not None else None

    async def get_by_checksum(
        self, owner_id: uuid.UUID, checksum: str
    ) -> Optional[JudicialNotificationDocumentModel]:
        return await self.session.scalar(
            select(JudicialNotificationDocumentModel)
            .join(
                DocumentModel,
                DocumentModel.id == JudicialNotificationDocumentModel.document_id,
            )
            .where(
                JudicialNotificationDocumentModel.judicial_notification_id == owner_id,
                DocumentModel.checksum == checksum,
                JudicialNotificationDocumentModel.deleted_at.is_(None),
            )
        )
