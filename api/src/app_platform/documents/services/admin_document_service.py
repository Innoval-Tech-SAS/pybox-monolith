import uuid
from datetime import datetime, timezone
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.documents.repository.document_repository import DocumentRepository
from app_platform.documents.schemas.admin_document_schemas import (
    TrashedDocumentDomain,
    TrashedDocumentListResponse,
    TrashedDocumentResponse,
)
from app_platform.documents.services.document_service import DocumentService
from app_platform.support.repository.ticket_document_repository import (
    TicketDocumentRepository,
)
from core.config.logger import logger
from receivables.debtors.repository.debtor_document_repository import (
    DebtorDocumentRepository,
)
from receivables.judicial_notifications.repository.judicial_notification_document_repository import (  # pylint: disable=line-too-long
    JudicialNotificationDocumentRepository,
)
from receivables.portfolios.repository.portfolio_document_repository import (
    PortfolioDocumentRepository,
)
from receivables.reports.repository.report_execution_repository import (
    ReportExecutionRepository,
)

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


class AdminDocumentService:
    """Papelera de documentos para Admin Global: listar lo dado de baja y restaurarlo.

    No tiene SQL propio. Orquesta los Repositories de cada dominio, que son los que
    saben de qué cuelga cada documento — exactamente la razón por la que la
    asociación polimórfica se reemplazó por una tabla de unión por relación: esta
    vista es el único lugar del sistema que necesita mirar las cinco a la vez, y lo
    hace con cinco consultas acotadas en vez de con un `WHERE ambito = ...` sobre
    una tabla gigante.

    El listado usa `get_deleted()` de `SoftDeleteRepositoryBase` (agregado para
    esto) y no `get_all_including_deleted()` filtrado en Python: filtrar en memoria
    obliga a traer la tabla completa para descartar casi todo, que es
    over-fetching sobre tablas de crecimiento no acotado. Con el
    `WHERE eliminado_en IS NOT NULL` en SQL, el motor devuelve solo el subconjunto
    chico que la papelera muestra.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._document_service = DocumentService(session)
        self._document_repo = DocumentRepository(session)
        self._debtor_repo = DebtorDocumentRepository(session)
        self._ticket_repo = TicketDocumentRepository(session)
        self._portfolio_repo = PortfolioDocumentRepository(session)
        self._judicial_repo = JudicialNotificationDocumentRepository(session)
        self._report_execution_repo = ReportExecutionRepository(session)

    # ── Listado ──────────────────────────────────────────────────────────────

    async def list_trash(self) -> TrashedDocumentListResponse:
        items: list[TrashedDocumentResponse] = []
        items.extend(await self._trashed_debtor_documents())
        items.extend(await self._trashed_ticket_documents())
        items.extend(await self._trashed_portfolio_documents())
        items.extend(await self._trashed_judicial_documents())
        items.extend(await self._trashed_report_executions())
        items.extend(await self._trashed_organization_documents())
        # Orden global por fecha de baja: la papelera se lee de lo más reciente a lo más
        # antiguo, y el orden de cada dominio por separado no alcanza para eso. El
        # fallback evita comparar None con datetime si alguna fila llegara sin fecha.
        items.sort(key=lambda item: item.deleted_at or _EPOCH, reverse=True)
        return TrashedDocumentListResponse(items=items, total=len(items))

    async def _trashed_debtor_documents(self) -> Sequence[TrashedDocumentResponse]:
        return [
            TrashedDocumentResponse(
                domain=TrashedDocumentDomain.DEBTOR,
                id=link.id,
                document_id=link.document_id,
                owner_id=link.debtor_id,
                category=link.category.value,
                deleted_at=link.deleted_at,
            )
            for link in await self._debtor_repo.get_deleted()
        ]

    async def _trashed_ticket_documents(self) -> Sequence[TrashedDocumentResponse]:
        return [
            TrashedDocumentResponse(
                domain=TrashedDocumentDomain.TICKET,
                id=link.id,
                document_id=link.document_id,
                owner_id=link.ticket_id,
                category=link.category.value,
                deleted_at=link.deleted_at,
            )
            for link in await self._ticket_repo.get_deleted()
        ]

    async def _trashed_portfolio_documents(self) -> Sequence[TrashedDocumentResponse]:
        return [
            TrashedDocumentResponse(
                domain=TrashedDocumentDomain.PORTFOLIO,
                id=link.id,
                document_id=link.document_id,
                owner_id=link.portfolio_id,
                category=link.category.value,
                deleted_at=link.deleted_at,
            )
            for link in await self._portfolio_repo.get_deleted()
        ]

    async def _trashed_judicial_documents(self) -> Sequence[TrashedDocumentResponse]:
        return [
            TrashedDocumentResponse(
                domain=TrashedDocumentDomain.JUDICIAL_NOTIFICATION,
                id=link.id,
                document_id=link.document_id,
                owner_id=link.judicial_notification_id,
                deleted_at=link.deleted_at,
            )
            for link in await self._judicial_repo.get_deleted()
        ]

    async def _trashed_report_executions(self) -> Sequence[TrashedDocumentResponse]:
        return [
            TrashedDocumentResponse(
                domain=TrashedDocumentDomain.REPORT_EXECUTION,
                id=execution.id,
                document_id=execution.document_id,
                owner_id=execution.report_id,
                original_name=execution.file_name,
                deleted_at=execution.deleted_at,
            )
            for execution in await self._report_execution_repo.get_deleted()
        ]

    async def _trashed_organization_documents(
        self,
    ) -> Sequence[TrashedDocumentResponse]:
        """Documentos sin tabla de unión que quedaron dados de baja en `documentos`.

        Son los casos 1:1 de la entidad (fiscal, mercantil, representante) y la foto
        de perfil: su baja la produce la sustitución del documento anterior, no un
        enlace de dominio. Acá el id de restauración ES el del propio documento.
        """
        return [
            TrashedDocumentResponse(
                domain=TrashedDocumentDomain.ORGANIZATION,
                id=document.id,
                document_id=document.id,
                owner_id=document.organization_id,
                original_name=document.original_name,
                deleted_at=document.deleted_at,
            )
            for document in await self._document_repo.get_deleted()
        ]

    # ── Restauración ─────────────────────────────────────────────────────────

    async def restore(
        self, domain: TrashedDocumentDomain, entity_id: uuid.UUID
    ) -> None:
        """Deshace la baja lógica del enlace de dominio y de su fila `documentos`.

        Alcanza con limpiar `eliminado_en` en las dos filas porque el borrado nunca
        toca el almacén: los bytes siguen ahí hasta que los barra el proceso de
        purga (fuera de este alcance).
        """
        if domain is TrashedDocumentDomain.ORGANIZATION:
            # Caso 1:1 sin enlace: el id es el del documento.
            document = await self._document_repo.get_by_id_including_deleted(entity_id)
            if document is None:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, "Documento no encontrado"
                )
            await self._document_service.restore(document)
            logger.info(
                "[documents] restaurado | dominio=%s documento=%s",
                domain.value,
                entity_id,
            )
            return

        repo = self._repo_for(domain)
        link = await repo.get_by_id_including_deleted(entity_id)
        if link is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado")
        await repo.restore(link)
        if link.document_id is not None:
            await self._document_service.restore_by_id(link.document_id)
        logger.info(
            "[documents] restaurado | dominio=%s enlace=%s documento=%s",
            domain.value,
            entity_id,
            link.document_id,
        )

    def _repo_for(self, domain: TrashedDocumentDomain):
        repos = {
            TrashedDocumentDomain.DEBTOR: self._debtor_repo,
            TrashedDocumentDomain.TICKET: self._ticket_repo,
            TrashedDocumentDomain.PORTFOLIO: self._portfolio_repo,
            TrashedDocumentDomain.JUDICIAL_NOTIFICATION: self._judicial_repo,
            TrashedDocumentDomain.REPORT_EXECUTION: self._report_execution_repo,
        }
        return repos[domain]
