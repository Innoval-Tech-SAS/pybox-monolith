import uuid
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.statements.models.statement_model import StatementModel


class StatementRepository(SoftDeleteRepositoryBase[StatementModel]):
    model_class = StatementModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    def _visible(self):
        return select(StatementModel).where(StatementModel.deleted_at.is_(None))

    async def list_by_debtor_and_portfolio(
        self, debtor_id: uuid.UUID, portfolio_id: uuid.UUID
    ) -> list[StatementModel]:
        result = await self.session.execute(
            self._visible()
            .where(
                StatementModel.debtor_id == debtor_id,
                StatementModel.portfolio_id == portfolio_id,
            )
            .order_by(StatementModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_by_debtor(self, debtor_ids: Sequence[uuid.UUID]) -> list[StatementModel]:
        """Extractos de las filas de deudor del titular (una por empresa) — para el
        portal del titular."""
        result = await self.session.execute(
            self._visible()
            .where(StatementModel.debtor_id.in_(debtor_ids))
            .order_by(StatementModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_owned_by_debtor(
        self, statement_id: uuid.UUID, debtor_ids: Sequence[uuid.UUID]
    ) -> Optional[StatementModel]:
        return await self.session.scalar(
            self._visible().where(
                StatementModel.id == statement_id,
                StatementModel.debtor_id.in_(debtor_ids),
            )
        )

    async def get_by_id_and_portfolio(
        self, statement_id: uuid.UUID, portfolio_id: uuid.UUID
    ) -> Optional[StatementModel]:
        return await self.session.scalar(
            self._visible().where(
                StatementModel.id == statement_id,
                StatementModel.portfolio_id == portfolio_id,
            )
        )

    async def soft_delete_by_organization(self, organization_id: uuid.UUID, deleted_at: datetime) -> None:
        """Baja en cascada de los extractos de la organización con el sello de la organización."""
        await self.soft_delete_where(StatementModel.organization_id == organization_id, deleted_at=deleted_at)

    async def restore_by_organization(self, organization_id: uuid.UUID, deleted_at: datetime) -> None:
        """Inverso de ``soft_delete_by_organization``: solo lo que cayó con la organización."""
        await self.restore_where(StatementModel.organization_id == organization_id, deleted_at=deleted_at)
