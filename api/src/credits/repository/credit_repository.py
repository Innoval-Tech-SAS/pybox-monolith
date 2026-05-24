import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.soft_delete_repository_base import SoftDeleteRepositoryBase
from credits.models.credit_model import CreditModel


class CreditRepository(SoftDeleteRepositoryBase[CreditModel]):
    model_class = CreditModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_credit_number(self, credit_number: str) -> CreditModel | None:
        result = await self.session.execute(
            select(CreditModel).where(
                CreditModel.credit_number == credit_number,
                CreditModel.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    async def get_by_portfolio_id(self, portfolio_id: uuid.UUID) -> list[CreditModel]:
        result = await self.session.execute(
            select(CreditModel).where(
                CreditModel.portfolio_id == portfolio_id,
                CreditModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_by_debtor_id(self, debtor_id: int) -> list[CreditModel]:
        result = await self.session.execute(
            select(CreditModel).where(
                CreditModel.debtor_id == debtor_id,
                CreditModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_by_codebtor_id(self, codebtor_id: int) -> list[CreditModel]:
        result = await self.session.execute(
            select(CreditModel).where(
                CreditModel.codebtor_id == codebtor_id,
                CreditModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())
