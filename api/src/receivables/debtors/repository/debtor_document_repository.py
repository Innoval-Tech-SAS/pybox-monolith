import uuid
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select

from app_platform.documents.models.document_model import DocumentModel
from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.debtors.enums.debtor_document_enums import DebtorDocumentCategory
from receivables.debtors.models.debtor_document_model import DebtorDocumentModel
from receivables.debtors.models.debtor_model import DebtorModel

# Prefijo del dominio en la clave del objeto (`<dominio>/<dueno>/<uuid><ext>`).
# Lo aporta el dominio dueño del documento; reemplaza a `DocumentOwnerScope.DEBTOR`, que
# desapareció junto con la asociación polimórfica.
DEBTOR_DOCUMENT_STORAGE_DOMAIN = "deudor"


class DebtorDocumentRepository(SoftDeleteRepositoryBase[DebtorDocumentModel]):
    """Documentos de un deudor.

    Todas las lecturas hacen el JOIN con `documentos` y devuelven las dos filas juntas:
    una fila de unión sin sus metadatos de archivo no sirve para nada, así que traerlas
    por separado sería un N+1 garantizado. Se devuelven como tupla en vez de vía
    `relationship` para que la carga sea siempre explícita y no haya lazy load (que en
    async revienta con MissingGreenlet).
    """

    model_class = DebtorDocumentModel

    def _visible_join(self):
        return (
            select(DebtorDocumentModel, DocumentModel)
            .join(DocumentModel, DocumentModel.id == DebtorDocumentModel.document_id)
            .where(
                DebtorDocumentModel.deleted_at.is_(None),
                DocumentModel.deleted_at.is_(None),
            )
        )

    async def list_by_debtor(
        self, debtor_id: uuid.UUID, category: Optional[DebtorDocumentCategory] = None
    ) -> Sequence[tuple[DebtorDocumentModel, DocumentModel]]:
        query = self._visible_join().where(DebtorDocumentModel.debtor_id == debtor_id)
        if category is not None:
            query = query.where(DebtorDocumentModel.category == category)
        result = await self.session.execute(
            query.order_by(DocumentModel.created_at.desc())
        )
        return list(result.all())

    async def get_owned(
        self, debtor_id: uuid.UUID, document_id: uuid.UUID
    ) -> Optional[tuple[DebtorDocumentModel, DocumentModel]]:
        """Documento solo si cuelga de ese deudor.

        Es el filtro que hace cumplir el ownership: si no es suyo el Service ve None y
        responde 404, sin confirmarle a quien pregunta que el documento existe.
        """
        row = (
            await self.session.execute(
                self._visible_join().where(
                    DebtorDocumentModel.debtor_id == debtor_id,
                    DebtorDocumentModel.document_id == document_id,
                )
            )
        ).first()
        return (row[0], row[1]) if row is not None else None

    async def get_by_checksum(
        self, owner_id: uuid.UUID, checksum: str
    ) -> Optional[DebtorDocumentModel]:
        """Mismo deudor y mismo contenido: el Service puede reusar esa fila en vez de
        guardar dos veces los mismos bytes. La dedup dejó de ser automática dentro de
        `DocumentService`: es el dominio el que decide si la quiere."""
        return await self.session.scalar(
            select(DebtorDocumentModel)
            .join(DocumentModel, DocumentModel.id == DebtorDocumentModel.document_id)
            .where(
                DebtorDocumentModel.debtor_id == owner_id,
                DocumentModel.checksum == checksum,
                DebtorDocumentModel.deleted_at.is_(None),
            )
        )

    async def soft_delete_by_organization(
        self, organization_id: uuid.UUID, deleted_at: datetime
    ) -> None:
        """Baja en cascada de los documentos de los deudores de la organización con
        el sello de la organización."""
        await self.soft_delete_where(
            DebtorDocumentModel.debtor_id.in_(
                select(DebtorModel.id).where(
                    DebtorModel.organization_id == organization_id
                )
            ),
            deleted_at=deleted_at,
        )

    async def restore_by_organization(
        self, organization_id: uuid.UUID, deleted_at: datetime
    ) -> None:
        """Inverso de ``soft_delete_by_organization``: solo lo que cayó con la
        organización."""
        await self.restore_where(
            DebtorDocumentModel.debtor_id.in_(
                select(DebtorModel.id).where(
                    DebtorModel.organization_id == organization_id
                )
            ),
            deleted_at=deleted_at,
        )
