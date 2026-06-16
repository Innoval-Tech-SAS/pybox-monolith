import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from receivables.contact_methods.models.contact_method_model import ContactMethodModel
from receivables.contact_methods.repository.contact_method_repository import ContactMethodRepository
from app_platform.countries.enums.country_enums import NATIONALITY_CURRENCY_CODE
from receivables.credits.models.credit_model import CreditModel
from receivables.credits.repository.credit_repository import CreditRepository
from receivables.debtors.models.address_model import AddressModel
from receivables.debtors.models.debtor_model import DebtorModel
from receivables.debtors.repository.address_repository import AddressRepository
from receivables.debtors.repository.debtor_repository import DebtorRepository
from receivables.debtors.schemas.debtor_schemas import (
    AddressResponse,
    ContactMethodResponse,
    CreateAddressRequest,
    CreateContactMethodRequest,
    CreateDebtorRequest,
    DebtorCreditResponse,
    DebtorDetailResponse,
    DebtorListResponse,
    DebtorResponse,
    RelatedContactsResponse,
)
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository
from core.security.permissions import PORTFOLIO_CLIENTS
from core.security.policies import require_permission
from core.security.services.encrypt_service import encrypt_service
from identity.users.schemas.user_session_schema import UserSession

from core.config.logger import logger


class DebtorService:
    def __init__(
        self,
        session: AsyncSession,
        debtor_repo: DebtorRepository,
        address_repo: AddressRepository,
        contact_repo: ContactMethodRepository,
        portfolio_repo: PortfolioRepository,
        credit_repo: CreditRepository,
    ) -> None:
        self._session = session
        self.debtor_repo = debtor_repo
        self.address_repo = address_repo
        self.contact_repo = contact_repo
        self.portfolio_repo = portfolio_repo
        self.credit_repo = credit_repo

    async def get_debtor(self, debtor_id: int, user_session: UserSession, portfolio_id: uuid.UUID | None) -> DebtorDetailResponse:
        if portfolio_id is not None:
            await self._check_portfolio_access(user_session, portfolio_id)
        debtor = await self._require_debtor(debtor_id)
        addresses = await self.address_repo.get_by_debtor_id(debtor_id)
        contacts = await self.contact_repo.get_by_debtor_id(debtor_id)
        return self._to_detail(debtor, addresses, contacts)

    async def list_debtors(
        self,
        user_session: UserSession,
        page: int,
        page_size: int,
        document_number: str | None,
        portfolio_id: uuid.UUID | None,
    ) -> DebtorListResponse:
        if portfolio_id is not None:
            await self._check_portfolio_access(user_session, portfolio_id)
        elif not user_session.is_global:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "portfolioId es requerido")

        doc_hash = encrypt_service.hash_document(document_number) if document_number else None
        items, total = await self.debtor_repo.list_paginated(
            page=page,
            page_size=page_size,
            document_number_hash=doc_hash,
            portfolio_id=portfolio_id,
        )
        return DebtorListResponse(
            items=[self._to_response(d) for d in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_related_contacts(
        self, debtor_id: int, portfolio_id: uuid.UUID, user_session: UserSession
    ) -> RelatedContactsResponse:
        await self._check_portfolio_access(user_session, portfolio_id)
        debtor = await self._require_debtor(debtor_id)

        # Solo créditos donde el deudor es titular — igual que pybox
        codebtor_ids_result = await self._session.execute(
            select(CreditModel.codebtor_id).where(
                CreditModel.debtor_id == debtor_id,
                CreditModel.codebtor_id.is_not(None),
                CreditModel.portfolio_id == portfolio_id,
                CreditModel.deleted_at.is_(None),
            ).distinct()
        )
        related_ids: set[int] = {cid for cid in codebtor_ids_result.scalars().all() if cid}

        primary_addresses = await self.address_repo.get_by_debtor_id(debtor_id)
        primary_contacts = await self.contact_repo.get_by_debtor_id(debtor_id)

        codebtors = []
        for rid in related_ids:
            rel = await self.debtor_repo.get_by_id(rid)
            if rel is None:
                continue
            rel_addresses = await self.address_repo.get_by_debtor_id(rid)
            rel_contacts = await self.contact_repo.get_by_debtor_id(rid)
            codebtors.append(self._to_detail(rel, rel_addresses, rel_contacts))

        return RelatedContactsResponse(
            debtor=self._to_detail(debtor, primary_addresses, primary_contacts),
            codebtors=codebtors,
        )

    async def get_debtor_credits(
        self, debtor_id: int, portfolio_id: uuid.UUID, user_session: UserSession
    ) -> list[DebtorCreditResponse]:
        await self._check_portfolio_access(user_session, portfolio_id)
        await self._require_debtor(debtor_id)
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if portfolio is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Portafolio no encontrado")
        currency_code = NATIONALITY_CURRENCY_CODE.get(portfolio.country, "COP")  # type: ignore[arg-type]
        credits = await self.credit_repo.get_by_debtor_and_portfolio(debtor_id, portfolio_id)
        return [
            DebtorCreditResponse(
                id=c.id,
                credit_number=c.credit_number,
                credit_type=c.credit_type,
                disbursed_date=c.disbursed_date,
                total_credit_balance=float(c.total_credit_balance),
                overdue_principal_balance=float(c.overdue_principal_balance),
                days_overdue_at_cutoff=c.days_overdue_at_cutoff,
                overdue_installments=c.overdue_installments,
                pending_installments=c.pending_installments,
                currency_code=currency_code,
            )
            for c in credits
        ]

    async def create_debtor(self, data: CreateDebtorRequest) -> DebtorModel:
        doc_hash = encrypt_service.hash_document(data.document_number)
        existing = await self.debtor_repo.get_by_document_number(doc_hash)
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, "El deudor ya existe")
        logger.info("[debtor] creando deudor | doc_type=%s", data.document_type)
        return await self.debtor_repo.add(
            DebtorModel(
                full_name=data.full_name,
                debtor_type=data.debtor_type,
                document_type=data.document_type,
                document_number=encrypt_service.encrypt_to_str(data.document_number),
                document_number_hash=doc_hash,
            )
        )

    async def create_address(self, debtor_id: int, data: CreateAddressRequest) -> AddressModel:
        await self._require_debtor(debtor_id)
        return await self.address_repo.add(
            AddressModel(
                debtor_id=debtor_id,
                address=data.address,
                city=data.city,
                state=data.state,
                country=data.country,
                address_type=data.address_type,
            )
        )

    async def create_contact_method(self, debtor_id: int, data: CreateContactMethodRequest) -> ContactMethodModel:
        await self._require_debtor(debtor_id)
        return await self.contact_repo.add(
            ContactMethodModel(
                debtor_id=debtor_id,
                contact_type=data.contact_type,
                contact_value=data.contact_value,
            )
        )

    async def _check_portfolio_access(self, user_session: UserSession, portfolio_id: uuid.UUID) -> None:
        if user_session.is_global:
            return
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if portfolio is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Portafolio no encontrado")
        require_permission(PORTFOLIO_CLIENTS, user_session, str(portfolio.organization_id))

    async def _require_debtor(self, debtor_id: int) -> DebtorModel:
        debtor = await self.debtor_repo.get_by_id(debtor_id)
        if debtor is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Deudor no encontrado")
        return debtor

    def _to_response(self, debtor: DebtorModel) -> DebtorResponse:
        return DebtorResponse(
            id=debtor.id,
            full_name=debtor.full_name,
            debtor_type=debtor.debtor_type,
            document_type=debtor.document_type,
            document_number=encrypt_service.decrypt_to_str(debtor.document_number),
        )

    def _to_detail(
        self,
        debtor: DebtorModel,
        addresses: list[AddressModel],
        contacts: list[ContactMethodModel],
    ) -> DebtorDetailResponse:
        return DebtorDetailResponse(
            id=debtor.id,
            full_name=debtor.full_name,
            debtor_type=debtor.debtor_type,
            document_type=debtor.document_type,
            document_number=encrypt_service.decrypt_to_str(debtor.document_number),
            addresses=[AddressResponse.model_validate(a) for a in addresses],
            contact_methods=[ContactMethodResponse.model_validate(c) for c in contacts],
        )
