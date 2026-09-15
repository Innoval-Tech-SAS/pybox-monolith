import uuid
from typing import Optional

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

    async def list_by_debtor(self, debtor_id: uuid.UUID) -> list[StatementModel]:
        """Extractos del deudor cruzando organizaciones — para el portal del titular."""
        result = await self.session.execute(
            self._visible()
            .where(StatementModel.debtor_id == debtor_id)
            .order_by(StatementModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_owned_by_debtor(
        self, statement_id: uuid.UUID, debtor_id: uuid.UUID
    ) -> Optional[StatementModel]:
        return await self.session.scalar(
            self._visible().where(
                StatementModel.id == statement_id,
                StatementModel.debtor_id == debtor_id,
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
