import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.countries.enums.country_enums import NATIONALITY_CURRENCY_CODE, UserDocumentType
from receivables.credits.repository.credit_repository import CreditRepository
from receivables.credits.schemas.my_credits_schemas import CreditWithPayments, PaymentSummary
from receivables.debtors.enums.debtor_enums import DebtorType
from receivables.debtors.repository.debtor_repository import DebtorRepository
from identity.organizations.repository.organization_repository import OrganizationRepository
from finance.payments.repository.payment_repository import PaymentRepository
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository
from core.security.services.encrypt_service import encrypt_service


class MyCreditsService:
    def __init__(self, session: AsyncSession) -> None:
        self._debtor_repo = DebtorRepository(session)
        self._credit_repo = CreditRepository(session)
        self._payment_repo = PaymentRepository(session)
        self._portfolio_repo = PortfolioRepository(session)
        self._org_repo = OrganizationRepository(session)

    async def get_my_credits(
        self, document_type: str, document_number: str
    ) -> list[CreditWithPayments]:
        try:
            doc_type = UserDocumentType(document_type)
        except ValueError:
            return []

        doc_hash = encrypt_service.hash_document(document_number)
        debtor = await self._debtor_repo.get_by_document(doc_type, doc_hash)
        if debtor is None:
            return []

        primary = await self._credit_repo.get_by_debtor_id(debtor.id)
        codebtor = await self._credit_repo.get_by_codebtor_id(debtor.id)

        all_credits = [(c, DebtorType.DEBTOR) for c in primary] + [
            (c, DebtorType.CO_DEBTOR) for c in codebtor
        ]

        if not all_credits:
            return []

        portfolio_ids: list[uuid.UUID] = list(
            {c.portfolio_id for c, _ in all_credits}
        )
        portfolios = await self._portfolio_repo.get_by_ids(portfolio_ids)
        portfolio_map = {p.id: p for p in portfolios}

        org_ids: list[uuid.UUID] = list(
            {p.organization_id for p in portfolio_map.values()}
        )
        orgs = await self._org_repo.get_by_ids(org_ids)
        org_map = {o.id: o.name for o in orgs}

        results: list[CreditWithPayments] = []
        for credit, role in all_credits:
            raw_payments = await self._payment_repo.get_by_credit_id(credit.id)
            payments = [
                PaymentSummary(
                    id=p.id,
                    limit_pay_date=p.limit_pay_date,
                    payment_date=p.payment_date,
                    payment_amount=float(p.payment_amount),
                    installment_number=p.installment_number,
                    principal_payment=float(p.principal_payment),
                    total_interest_amount=float(p.total_interest_amount),
                    other_charges=float(p.other_charges),
                )
                for p in raw_payments
            ]

            portfolio = portfolio_map[credit.portfolio_id]
            org_name = org_map.get(portfolio.organization_id, "")
            currency_code = NATIONALITY_CURRENCY_CODE[portfolio.country]  # type: ignore[index]

            results.append(
                CreditWithPayments(
                    id=credit.id,
                    credit_number=credit.credit_number,
                    credit_type=credit.credit_type,
                    disbursed_date=credit.disbursed_date,
                    total_credit_balance=float(credit.total_credit_balance),
                    overdue_principal_balance=float(credit.overdue_principal_balance),
                    days_overdue_at_cutoff=credit.days_overdue_at_cutoff,
                    role=role,
                    organization_name=org_name or "",
                    currency_code=currency_code,
                    payments=payments,
                )
            )

        return results
