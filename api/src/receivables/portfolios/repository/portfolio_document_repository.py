"""Acceso a datos de los documentos asociados a un portafolio."""

import uuid
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select

from app_platform.documents.models.document_model import DocumentModel
from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.portfolios.enums.portfolio_document_enums import (
    PortfolioDocumentCategory,
)
from receivables.portfolios.models.portfolio_document_model import (
    PortfolioDocumentModel,
)

# Prefijo del dominio en la clave del objeto (`<dominio>/<dueno>/<uuid><ext>`).
# Lo aporta el dominio dueño del documento; reemplaza a
# `DocumentOwnerScope.PORTFOLIO`, que desapareció junto con la asociación
# polimórfica.
PORTFOLIO_DOCUMENT_STORAGE_DOMAIN = "portafolio"


class PortfolioDocumentRepository(SoftDeleteRepositoryBase[PortfolioDocumentModel]):
    """Archivos asociados a un portafolio. Mismo criterio que
    `DebtorDocumentRepository`: el JOIN con `documentos` va en la query, no en un
    lazy load."""

    model_class = PortfolioDocumentModel

    def _visible_join(self):
        return (
            select(PortfolioDocumentModel, DocumentModel)
            .join(DocumentModel, DocumentModel.id == PortfolioDocumentModel.document_id)
            .where(
                PortfolioDocumentModel.deleted_at.is_(None),
                DocumentModel.deleted_at.is_(None),
            )
        )

    async def list_by_portfolio(
        self,
        portfolio_id: uuid.UUID,
        category: Optional[PortfolioDocumentCategory] = None,
    ) -> Sequence[tuple[PortfolioDocumentModel, DocumentModel]]:
        query = self._visible_join().where(
            PortfolioDocumentModel.portfolio_id == portfolio_id
        )
        if category is not None:
            query = query.where(PortfolioDocumentModel.category == category)
        result = await self.session.execute(
            query.order_by(DocumentModel.created_at.desc())
        )
        return list(result.all())

    async def get_owned(
        self, portfolio_id: uuid.UUID, document_id: uuid.UUID
    ) -> Optional[tuple[PortfolioDocumentModel, DocumentModel]]:
        row = (
            await self.session.execute(
                self._visible_join().where(
                    PortfolioDocumentModel.portfolio_id == portfolio_id,
                    PortfolioDocumentModel.document_id == document_id,
                )
            )
        ).first()
        return (row[0], row[1]) if row is not None else None

    async def get_by_checksum(
        self, owner_id: uuid.UUID, checksum: str
    ) -> Optional[PortfolioDocumentModel]:
        return await self.session.scalar(
            select(PortfolioDocumentModel)
            .join(DocumentModel, DocumentModel.id == PortfolioDocumentModel.document_id)
            .where(
                PortfolioDocumentModel.portfolio_id == owner_id,
                DocumentModel.checksum == checksum,
                PortfolioDocumentModel.deleted_at.is_(None),
            )
        )

    async def soft_delete_by_organization(
        self, organization_id: uuid.UUID, deleted_at: datetime
    ) -> None:
        """Baja en cascada de los documentos de portafolio de la organización con
        el sello de la organización."""
        await self.soft_delete_where(
            PortfolioDocumentModel.organization_id == organization_id,
            deleted_at=deleted_at,
        )

    async def restore_by_organization(
        self, organization_id: uuid.UUID, deleted_at: datetime
    ) -> None:
        """Inverso de ``soft_delete_by_organization``: solo lo que cayó con la
        organización."""
        await self.restore_where(
            PortfolioDocumentModel.organization_id == organization_id,
            deleted_at=deleted_at,
        )
