import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from app_platform.countries.enums.country_enums import UserDocumentType
from receivables.credits.models.credit_model import CreditModel
from receivables.debtors.models.debtor_model import DebtorModel


class DebtorRepository(SoftDeleteRepositoryBase[DebtorModel]):
    model_class = DebtorModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_document(
        self, document_type: UserDocumentType, document_number_hash: str
    ) -> DebtorModel | None:
        result = await self.session.execute(
            select(DebtorModel).where(
                DebtorModel.document_type == document_type,
                DebtorModel.document_number_hash == document_number_hash,
                DebtorModel.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    async def get_by_document_number(self, document_number_hash: str) -> DebtorModel | None:
        result = await self.session.execute(
            select(DebtorModel).where(
                DebtorModel.document_number_hash == document_number_hash,
                DebtorModel.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    async def list_paginated(
        self,
        page: int,
        page_size: int,
        document_number_hash: str | None = None,
        portfolio_id: uuid.UUID | None = None,
    ) -> tuple[list[DebtorModel], int]:
        query = select(DebtorModel).where(DebtorModel.deleted_at.is_(None))

        if document_number_hash is not None:
            query = query.where(DebtorModel.document_number_hash == document_number_hash)

        if portfolio_id is not None:
            query = (
                query
                .join(
                    CreditModel,
                    or_(
                        CreditModel.debtor_id == DebtorModel.id,
                        CreditModel.codebtor_id == DebtorModel.id,
                    ),
                )
                .where(
                    CreditModel.portfolio_id == portfolio_id,
                    CreditModel.deleted_at.is_(None),
                )
                .distinct()
            )

        total: int = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        ) or 0

        result = await self.session.execute(
            query.offset((page - 1) * page_size).limit(page_size)
        )
        return list(result.scalars().all()), total
