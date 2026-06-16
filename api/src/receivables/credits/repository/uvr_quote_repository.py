from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.credits.models.uvr_quote_model import UVRQuoteModel


class UVRQuoteRepository(SoftDeleteRepositoryBase[UVRQuoteModel]):
    model_class = UVRQuoteModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_credit_id(self, credit_id: int) -> list[UVRQuoteModel]:
        result = await self.session.execute(
            select(UVRQuoteModel).where(
                UVRQuoteModel.credit_id == credit_id,
                UVRQuoteModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_by_date(self, quote_date: datetime) -> UVRQuoteModel | None:
        result = await self.session.execute(
            select(UVRQuoteModel).where(
                UVRQuoteModel.quote_date == quote_date,
                UVRQuoteModel.deleted_at.is_(None),
            )
        )
        return result.scalars().first()
