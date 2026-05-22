from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base.soft_delete_repository_base import SoftDeleteRepositoryBase
from debtors.enums.debtor_enums import DocumentTypes
from debtors.models.debtor_model import DebtorModel


class DebtorRepository(SoftDeleteRepositoryBase[DebtorModel]):
    model_class = DebtorModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_document(
        self, document_type: DocumentTypes, document_number: str
    ) -> DebtorModel | None:
        result = await self.session.execute(
            select(DebtorModel).where(
                DebtorModel.document_type == document_type,
                DebtorModel.document_number == document_number,
                DebtorModel.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    async def get_by_document_number(self, document_number: str) -> DebtorModel | None:
        result = await self.session.execute(
            select(DebtorModel).where(
                DebtorModel.document_number == document_number,
                DebtorModel.deleted_at.is_(None),
            )
        )
        return result.scalars().first()
