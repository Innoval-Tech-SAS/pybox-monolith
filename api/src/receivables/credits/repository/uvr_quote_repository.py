"""Acceso a datos de las cotizaciones históricas de UVR."""

import uuid
from datetime import datetime

from sqlalchemy import select

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.credits.models.uvr_quote_model import UVRQuoteModel


class UVRQuoteRepository(SoftDeleteRepositoryBase[UVRQuoteModel]):
    model_class = UVRQuoteModel

    async def get_by_credit_id(self, credit_id: uuid.UUID) -> list[UVRQuoteModel]:
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
