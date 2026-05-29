import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime

from config.paths import UPLOADS_ROOT

from sqlalchemy.ext.asyncio import AsyncSession
from countries.enums.country_enums import Nationality

logger = logging.getLogger(__name__)

from contact_methods.models.contact_method_model import ContactMethodModel
from contact_methods.repository.contact_method_repository import ContactMethodRepository
from credits.models.credit_adjustment_model import CreditAdjustmentModel
from credits.models.credit_model import CreditModel
from credits.models.uvr_quote_model import UVRQuoteModel
from credits.repository.credit_adjustment_repository import CreditAdjustmentRepository
from credits.repository.credit_repository import CreditRepository
from credits.repository.uvr_quote_repository import UVRQuoteRepository
from debtors.models.address_model import AddressModel
from debtors.models.debtor_model import DebtorModel
from debtors.repository.address_repository import AddressRepository
from debtors.repository.debtor_repository import DebtorRepository
from payments.models.payment_model import PaymentModel
from payments.repository.payment_repository import PaymentRepository
from portfolios.models.portfolio_model import PortfolioModel
from portfolios.repository.portfolio_repository import PortfolioRepository
from security.services.encrypt_service import encrypt_service
from portfolios.utils.portfolio_file_parser import (
    AddressRowData,
    CreditAdjustmentRowData,
    CreditRowData,
    DebtorRowData,
    PaymentRowData,
    PortfolioFileParser,
    PortfolioRowData,
    UVRQuoteRowData,
)

_MAX_ERRORS = 50


@dataclass
class CsvProcessResult:
    total_rows: int
    processed_rows: int
    failed_rows: int
    portfolio_id: uuid.UUID
    titulares: int
    codeudores: int
    creditos: int
    clientes_unicos: int
    errors: list[str] = field(default_factory=list)


class PortfolioCsvService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.parser = PortfolioFileParser()
        self.portfolio_repo = PortfolioRepository(session)
        self.debtor_repo = DebtorRepository(session)
        self.address_repo = AddressRepository(session)
        self.contact_method_repo = ContactMethodRepository(session)
        self.credit_repo = CreditRepository(session)
        self.payment_repo = PaymentRepository(session)
        self.uvr_quote_repo = UVRQuoteRepository(session)
        self.credit_adjustment_repo = CreditAdjustmentRepository(session)

    async def process_csv(
        self,
        file_bytes: bytes,
        organization_id: uuid.UUID,
        portfolio_name: str | None = None,
        country: Nationality | None = None,
        filename: str = "",
    ) -> CsvProcessResult:
        logger.info("[process_csv] START | org=%s nombre=%s bytes=%d", organization_id, portfolio_name, len(file_bytes))

        file_data = self.parser.parse(file_bytes, filename)
        logger.info("[process_csv] parsed | filas=%d skipped=%d", len(file_data.rows), file_data.total_skipped)

        portfolio = await self.portfolio_repo.add(
            PortfolioModel(
                name=portfolio_name or f"Portafolio {organization_id}",
                organization_id=organization_id,
                country=country,
            )
        )
        logger.info("[process_csv] portfolio creado | id=%s", portfolio.id)

        ext = "xlsx" if filename.lower().endswith(".xlsx") else "csv"
        portfolio_dir = os.path.join(UPLOADS_ROOT, "organizations", str(organization_id), "portfolios")
        os.makedirs(portfolio_dir, exist_ok=True)
        dest_path = os.path.join(portfolio_dir, f"{portfolio.id}.{ext}")
        with open(dest_path, "wb") as fh:
            fh.write(file_bytes)
        logger.info("[process_csv] archivo guardado | path=%s", dest_path)

        total_rows = len(file_data.rows) + file_data.total_skipped

        titulares_docs = {
            (r.debtor.document_type, encrypt_service.hash_document(r.debtor.document_number))
            for r in file_data.rows
        }
        codeudores_docs = {
            (r.codebtor.document_type, encrypt_service.hash_document(r.codebtor.document_number))
            for r in file_data.rows
            if r.codebtor
        }

        processed = 0
        errors: list[str] = []

        for idx, row in enumerate(file_data.rows, start=1):
            error = await self._process_row(row, portfolio.id, idx)
            if error:
                if len(errors) < _MAX_ERRORS:
                    errors.append(error)
            else:
                processed += 1

        failed = len(file_data.rows) - processed
        result = CsvProcessResult(
            total_rows=total_rows,
            processed_rows=processed,
            failed_rows=failed,
            portfolio_id=portfolio.id,
            titulares=len(titulares_docs),
            codeudores=len(codeudores_docs),
            creditos=len(file_data.rows),
            clientes_unicos=len(titulares_docs),
            errors=errors,
        )
        logger.info("[process_csv] END | procesados=%d fallidos=%d total=%d", processed, failed, total_rows)
        return result

    # ------------------------------------------------------------------
    # Row processor
    # ------------------------------------------------------------------

    async def _process_row(
        self, row: PortfolioRowData, portfolio_id: uuid.UUID, row_number: int
    ) -> str | None:
        logger.debug("[_process_row] START | fila=%d doc=%s", row_number, row.debtor.document_number)
        try:
            async with self.session.begin_nested():
                debtor = await self._upsert_debtor(row.debtor)
                codebtor = (
                    await self._upsert_debtor(row.codebtor) if row.codebtor else None
                )
                await self._upsert_address(debtor.id, row.primary_address)
                if row.secondary_address:
                    await self._upsert_address(debtor.id, row.secondary_address)
                await self._upsert_contact_methods(debtor.id, row.debtor_contacts)
                if codebtor and row.codebtor_contacts:
                    await self._upsert_contact_methods(codebtor.id, row.codebtor_contacts)
                credit = await self._upsert_credit(
                    row.credit,
                    portfolio_id,
                    debtor.id,
                    codebtor.id if codebtor else None,
                )
                if row.payment:
                    await self._insert_payment(credit.id, row.payment)
                if row.uvr_quote:
                    await self._insert_uvr_quote(credit.id, row.uvr_quote)
                if row.credit_adjustment:
                    await self._insert_credit_adjustment(credit.id, row.credit_adjustment)
        except Exception as exc:
            logger.warning("[_process_row] ERROR | fila=%d doc=%s error=%s", row_number, row.debtor.document_number, exc)
            return f"Fila {row_number} (doc: {row.debtor.document_number}): {exc}"
        logger.debug("[_process_row] END OK | fila=%d", row_number)
        return None

    # ------------------------------------------------------------------
    # Upsert helpers
    # ------------------------------------------------------------------

    async def _upsert_debtor(self, data: DebtorRowData) -> DebtorModel:
        logger.debug("[_upsert_debtor] START | doc=%s", data.document_number)
        doc_hash = encrypt_service.hash_document(data.document_number)
        existing = await self.debtor_repo.get_by_document_number(doc_hash)
        if existing:
            existing.full_name = data.full_name
            existing.document_type = data.document_type
            result = await self.debtor_repo.update(existing)
            logger.debug("[_upsert_debtor] END updated | id=%d", result.id)
            return result
        result = await self.debtor_repo.add(
            DebtorModel(
                document_number=encrypt_service.encrypt_to_str(data.document_number),
                document_number_hash=doc_hash,
                full_name=data.full_name,
                document_type=data.document_type,
                debtor_type=data.debtor_type,
            )
        )
        logger.debug("[_upsert_debtor] END created | id=%d", result.id)
        return result

    async def _upsert_address(self, debtor_id: int, data: AddressRowData) -> None:
        logger.debug("[_upsert_address] START | debtor_id=%d type=%s", debtor_id, data.address_type)
        existing_list = await self.address_repo.get_by_debtor_id(debtor_id)
        existing = next(
            (a for a in existing_list if a.address_type == data.address_type), None
        )
        if existing:
            existing.address = data.address
            existing.city = data.city
            existing.state = data.state
            existing.country = data.country
            await self.address_repo.update(existing)
        else:
            await self.address_repo.add(
                AddressModel(
                    debtor_id=debtor_id,
                    address=data.address,
                    city=data.city,
                    state=data.state,
                    country=data.country,
                    address_type=data.address_type,
                )
            )

    async def _upsert_contact_methods(
        self, debtor_id: int, contacts: list
    ) -> None:
        logger.debug("[_upsert_contact_methods] START | debtor_id=%d count=%d", debtor_id, len(contacts))
        existing_list = await self.contact_method_repo.get_by_debtor_id(debtor_id)
        existing_by_type = {c.contact_type: c for c in existing_list}
        for contact_data in contacts:
            if contact_data.contact_type in existing_by_type:
                record = existing_by_type[contact_data.contact_type]
                record.contact_value = contact_data.contact_value
                await self.contact_method_repo.update(record)
            else:
                await self.contact_method_repo.add(
                    ContactMethodModel(
                        debtor_id=debtor_id,
                        contact_type=contact_data.contact_type,
                        contact_value=contact_data.contact_value,
                    )
                )
        logger.debug("[_upsert_contact_methods] END | debtor_id=%d", debtor_id)

    async def _upsert_credit(
        self,
        data: CreditRowData,
        portfolio_id: uuid.UUID,
        debtor_id: int,
        codebtor_id: int | None,
    ) -> CreditModel:
        logger.debug("[_upsert_credit] START | credit_number=%s debtor_id=%d", data.credit_number, debtor_id)
        fields = dict(
            credit_number=data.credit_number,
            credit_date=data.credit_date,
            disbursed_date=data.disbursed_date,
            credit_type=data.credit_type,
            agreed_interest_rate=data.agreed_interest_rate,
            charged_effective_annual_rate=data.charged_effective_annual_rate,
            balance_disbursed=data.balance_disbursed,
            court_date=data.court_date,
            initial_term=data.initial_term,
            total_credit_balance=data.total_credit_balance,
            overdue_principal_balance=data.overdue_principal_balance,
            current_interest=data.current_interest,
            overdue_interest=data.overdue_interest,
            other_concepts=data.other_concepts,
            overdue_installments=data.overdue_installments,
            days_overdue_at_cutoff=data.days_overdue_at_cutoff,
            amortization_system=data.amortization_system,
            pending_installments=data.pending_installments,
            insurance_total=data.insurance_total,
            commission_accum=data.commission_accum,
            platform_fee_accum=data.platform_fee_accum,
            vat_accum=data.vat_accum,
            subproduct=data.subproduct,
            uvr_last_quote=data.uvr_last_quote,
            condonations_accum=data.condonations_accum,
            portfolio_id=portfolio_id,
            debtor_id=debtor_id,
            codebtor_id=codebtor_id,
        )
        existing = await self.credit_repo.get_by_credit_number(data.credit_number)
        if existing:
            for attr, val in fields.items():
                setattr(existing, attr, val)
            result = await self.credit_repo.update(existing)
            logger.debug("[_upsert_credit] END updated | id=%d", result.id)
            return result
        result = await self.credit_repo.add(CreditModel(**fields))
        logger.debug("[_upsert_credit] END created | id=%d", result.id)
        return result

    async def _insert_payment(self, credit_id: int, data: PaymentRowData) -> None:
        logger.debug("[_insert_payment] START | credit_id=%d", credit_id)
        insurances_total = data.life_insurance_charge + data.vehicle_insurance_charge
        total_interest = data.current_interest_amount + data.overdue_interest_amount
        await self.payment_repo.add(
            PaymentModel(
                credit_id=credit_id,
                payment_date=data.payment_date,
                limit_pay_date=data.limit_pay_date,
                payment_amount=float(data.payment_amount),
                installment_number=data.installment_number,
                principal_payment=float(data.principal_payment),
                current_interest_amount=float(data.current_interest_amount),
                overdue_interest_amount=float(data.overdue_interest_amount),
                life_insurance_charge=float(data.life_insurance_charge),
                vehicle_insurance_charge=float(data.vehicle_insurance_charge),
                insurances_total=float(insurances_total),
                other_charges=float(data.other_charges),
                total_interest_amount=float(total_interest),
                other_concepts_amount=0.0,
                vat=float(data.vat),
                commission_amount=float(data.commission_amount),
                platform_fee=float(data.platform_fee),
                condonation_amount=0.0,
                discount_amount=0.0,
            )
        )
        logger.debug("[_insert_payment] END | credit_id=%d", credit_id)

    async def _insert_uvr_quote(self, credit_id: int, data: UVRQuoteRowData) -> None:
        logger.debug("[_insert_uvr_quote] START | credit_id=%d", credit_id)
        await self.uvr_quote_repo.add(
            UVRQuoteModel(
                credit_id=credit_id,
                quote_value=float(data.quote_value),
                quote_date=data.quote_date,
            )
        )
        logger.debug("[_insert_uvr_quote] END | credit_id=%d", credit_id)

    async def _insert_credit_adjustment(
        self, credit_id: int, data: CreditAdjustmentRowData
    ) -> None:
        logger.debug("[_insert_credit_adjustment] START | credit_id=%d type=%s", credit_id, data.adjustment_type)
        await self.credit_adjustment_repo.add(
            CreditAdjustmentModel(
                credit_id=credit_id,
                adjustment_type=data.adjustment_type,
                adjustment_amount=float(data.adjustment_amount),
                applied_date=data.applied_date,
            )
        )
        logger.debug("[_insert_credit_adjustment] END | credit_id=%d", credit_id)

    # ------------------------------------------------------------------
    # Append mode — agrega datos a portafolio existente (upsert)
    # ------------------------------------------------------------------

    async def append_csv(
        self,
        portfolio_id: uuid.UUID,
        file_bytes: bytes,
        filename: str = "",
    ) -> CsvProcessResult:
        logger.info("[append_csv] START | portfolio=%s bytes=%d", portfolio_id, len(file_bytes))
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if portfolio is None:
            raise ValueError(f"Portafolio {portfolio_id} no encontrado")

        file_data = self.parser.parse(file_bytes, filename)
        logger.info("[append_csv] parsed | filas=%d skipped=%d", len(file_data.rows), file_data.total_skipped)

        ext = "xlsx" if filename.lower().endswith(".xlsx") else "csv"
        portfolio_dir = os.path.join(UPLOADS_ROOT, "organizations", str(portfolio.organization_id), "portfolios")
        os.makedirs(portfolio_dir, exist_ok=True)
        ts = int(datetime.utcnow().timestamp())
        with open(os.path.join(portfolio_dir, f"{portfolio.id}_append_{ts}.{ext}"), "wb") as fh:
            fh.write(file_bytes)

        titulares_docs = {
            (r.debtor.document_type, encrypt_service.hash_document(r.debtor.document_number))
            for r in file_data.rows
        }
        codeudores_docs = {
            (r.codebtor.document_type, encrypt_service.hash_document(r.codebtor.document_number))
            for r in file_data.rows
            if r.codebtor
        }

        total_rows = len(file_data.rows) + file_data.total_skipped
        processed = 0
        errors: list[str] = []

        for idx, row in enumerate(file_data.rows, start=1):
            error = await self._process_row(row, portfolio.id, idx)
            if error:
                if len(errors) < _MAX_ERRORS:
                    errors.append(error)
            else:
                processed += 1

        failed = len(file_data.rows) - processed
        result = CsvProcessResult(
            total_rows=total_rows,
            processed_rows=processed,
            failed_rows=failed,
            portfolio_id=portfolio.id,
            titulares=len(titulares_docs),
            codeudores=len(codeudores_docs),
            creditos=len(file_data.rows),
            clientes_unicos=len(titulares_docs),
            errors=errors,
        )
        logger.info("[append_csv] END | procesados=%d fallidos=%d", processed, failed)
        return result

    # ------------------------------------------------------------------
    # Update mode — reemplaza todos los créditos del portafolio
    # ------------------------------------------------------------------

    async def update_csv(
        self,
        portfolio_id: uuid.UUID,
        file_bytes: bytes,
        filename: str = "",
    ) -> CsvProcessResult:
        logger.info("[update_csv] START | portfolio=%s bytes=%d", portfolio_id, len(file_bytes))
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if portfolio is None:
            raise ValueError(f"Portafolio {portfolio_id} no encontrado")

        existing_credits = await self.credit_repo.get_by_portfolio_id(portfolio_id)
        logger.info("[update_csv] eliminando %d créditos existentes", len(existing_credits))
        for credit in existing_credits:
            await self.credit_repo.delete(credit)

        file_data = self.parser.parse(file_bytes, filename)
        logger.info("[update_csv] parsed | filas=%d skipped=%d", len(file_data.rows), file_data.total_skipped)

        ext = "xlsx" if filename.lower().endswith(".xlsx") else "csv"
        portfolio_dir = os.path.join(UPLOADS_ROOT, "organizations", str(portfolio.organization_id), "portfolios")
        os.makedirs(portfolio_dir, exist_ok=True)
        ts = int(datetime.utcnow().timestamp())
        with open(os.path.join(portfolio_dir, f"{portfolio.id}_update_{ts}.{ext}"), "wb") as fh:
            fh.write(file_bytes)

        titulares_docs = {
            (r.debtor.document_type, encrypt_service.hash_document(r.debtor.document_number))
            for r in file_data.rows
        }
        codeudores_docs = {
            (r.codebtor.document_type, encrypt_service.hash_document(r.codebtor.document_number))
            for r in file_data.rows
            if r.codebtor
        }

        total_rows = len(file_data.rows) + file_data.total_skipped
        processed = 0
        errors: list[str] = []

        for idx, row in enumerate(file_data.rows, start=1):
            error = await self._process_row(row, portfolio.id, idx)
            if error:
                if len(errors) < _MAX_ERRORS:
                    errors.append(error)
            else:
                processed += 1

        failed = len(file_data.rows) - processed
        result = CsvProcessResult(
            total_rows=total_rows,
            processed_rows=processed,
            failed_rows=failed,
            portfolio_id=portfolio.id,
            titulares=len(titulares_docs),
            codeudores=len(codeudores_docs),
            creditos=len(file_data.rows),
            clientes_unicos=len(titulares_docs),
            errors=errors,
        )
        logger.info("[update_csv] END | procesados=%d fallidos=%d", processed, failed)
        return result
