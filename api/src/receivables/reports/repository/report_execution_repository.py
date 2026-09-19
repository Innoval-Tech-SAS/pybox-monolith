import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.reports.models.report_execution_model import ReportExecutionModel

# Prefijo del dominio en la clave del objeto (`<dominio>/<dueno>/<uuid><ext>`). El dueño
# del CSV de auditoría es la entidad que ejecutó el reporte; reemplaza a
# `DocumentOwnerScope.ORGANIZATION` con categoría `REPORTE`.
REPORT_DOCUMENT_STORAGE_DOMAIN = "entidad_reporte"


class ReportExecutionRepository(SoftDeleteRepositoryBase[ReportExecutionModel]):
    """Ejecuciones de reporte.

    Extiende `SoftDeleteRepositoryBase` y no `RepositoryBase` porque el modelo ya tiene
    `eliminado_en` y ahora es dueño de un documento: la papelera de Admin Global tiene que
    poder listarlo y restaurarlo con la misma semántica que las tablas de unión. Nadie
    llamaba a `delete()` de este repo, así que el cambio de borrado físico a lógico no
    altera ningún flujo existente.
    """

    model_class = ReportExecutionModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_report(self, report_id: uuid.UUID) -> Sequence[ReportExecutionModel]:
        result = await self.session.execute(
            select(ReportExecutionModel)
            .where(
                ReportExecutionModel.report_id == report_id,
                ReportExecutionModel.deleted_at.is_(None),
            )
            .order_by(ReportExecutionModel.created_at.desc())
        )
        return result.scalars().all()
