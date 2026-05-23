from sqlalchemy.ext.asyncio import AsyncSession

from countries.enums.country_enums import UserDocumentType
from credits.repository.credit_repository import CreditRepository
from credits.schemas.my_credits_schemas import MyCreditResponse
from debtors.enums.debtor_enums import DebtorType
from debtors.repository.debtor_repository import DebtorRepository
from security.services.encrypt_service import encrypt_service


class MyCreditsService:
    def __init__(self, session: AsyncSession) -> None:
        self._debtor_repo = DebtorRepository(session)
        self._credit_repo = CreditRepository(session)

    async def get_my_credits(
        self, document_type: str, document_number: str
    ) -> list[MyCreditResponse]:
        try:
            doc_type = UserDocumentType(document_type)
        except ValueError:
            return []

        doc_hash = encrypt_service.hash_document(document_number)
        debtor = await self._debtor_repo.get_by_document(doc_type, doc_hash)
        if debtor is None:
            return []

        results: list[MyCreditResponse] = []

        primary_credits = await self._credit_repo.get_by_debtor_id(debtor.id)
        for credit in primary_credits:
            results.append(MyCreditResponse(
                id=credit.id,
                credit_number=credit.credit_number,
                credit_type=credit.credit_type,
                credit_date=credit.credit_date,
                disbursed_date=credit.disbursed_date,
                court_date=credit.court_date,
                total_credit_balance=float(credit.total_credit_balance),
                overdue_principal_balance=float(credit.overdue_principal_balance),
                current_interest=float(credit.current_interest),
                overdue_interest=float(credit.overdue_interest),
                days_overdue_at_cutoff=credit.days_overdue_at_cutoff,
                overdue_installments=credit.overdue_installments,
                pending_installments=credit.pending_installments,
                role=DebtorType.DEBTOR,
            ))

        codebtor_credits = await self._credit_repo.get_by_codebtor_id(debtor.id)
        for credit in codebtor_credits:
            results.append(MyCreditResponse(
                id=credit.id,
                credit_number=credit.credit_number,
                credit_type=credit.credit_type,
                credit_date=credit.credit_date,
                disbursed_date=credit.disbursed_date,
                court_date=credit.court_date,
                total_credit_balance=float(credit.total_credit_balance),
                overdue_principal_balance=float(credit.overdue_principal_balance),
                current_interest=float(credit.current_interest),
                overdue_interest=float(credit.overdue_interest),
                days_overdue_at_cutoff=credit.days_overdue_at_cutoff,
                overdue_installments=credit.overdue_installments,
                pending_installments=credit.pending_installments,
                role=DebtorType.CO_DEBTOR,
            ))

        return results
