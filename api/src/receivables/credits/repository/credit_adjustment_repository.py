"""Acceso a datos de los ajustes manuales aplicados a un crédito."""

import uuid

from sqlalchemy import select

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.credits.models.credit_adjustment_model import CreditAdjustmentModel


class CreditAdjustmentRepository(SoftDeleteRepositoryBase[CreditAdjustmentModel]):
    model_class = CreditAdjustmentModel

    async def get_by_credit_id(
        self, credit_id: uuid.UUID
    ) -> list[CreditAdjustmentModel]:
        result = await self.session.execute(
            select(CreditAdjustmentModel).where(
                CreditAdjustmentModel.credit_id == credit_id,
                CreditAdjustmentModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())
