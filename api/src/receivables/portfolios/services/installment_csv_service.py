"""Carga del plan de cuotas por CSV/XLSX — feature separada del importador grande de
portafolio (`portfolio_csv_service.py`). No depende de él ni comparte sus modelos de
fila a propósito: identifica créditos ya existentes por `Numero de credito` y
crea/actualiza cuotas (`PaymentModel`) sobre ellos, sin tocar deudores/direcciones/etc.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.documents.enums.document_enums import (
    CSV_CONTENT_TYPE,
    XLSX_CONTENT_TYPE,
)
from app_platform.documents.services.document_service import DocumentService
from core.config.logger import logger
from core.tools.config_tools import get_or_default
from receivables.credits.models.credit_model import CreditModel
from receivables.credits.repository.credit_repository import CreditRepository
from receivables.payments.enums.payment_enums import PaymentStatus
from receivables.payments.models.payment_model import PaymentModel
from receivables.payments.repository.payment_repository import PaymentRepository
from receivables.portfolios.constants.portfolio_csv_constants import (
    DEFAULT_PORTFOLIO_CSV_BULK_UPSERT,
    MAX_ERRORS,
    PORTFOLIO_CSV_BULK_UPSERT_ENV_VAR,
)
from receivables.portfolios.enums.portfolio_document_enums import (
    PortfolioDocumentCategory,
)
from receivables.portfolios.models.portfolio_document_model import (
    PortfolioDocumentModel,
)
from receivables.portfolios.models.portfolio_model import PortfolioModel
from receivables.portfolios.repository.portfolio_document_repository import (
    PORTFOLIO_DOCUMENT_STORAGE_DOMAIN,
    PortfolioDocumentRepository,
)
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository
from receivables.portfolios.schemas.portfolio_csv_schemas import (
    InstallmentsUploadResult,
)
from receivables.portfolios.schemas.portfolio_file_schemas import InstallmentRowData
from receivables.portfolios.utils.installment_file_parser import InstallmentFileParser


class InstallmentCsvService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.parser = InstallmentFileParser()
        self.portfolio_repo = PortfolioRepository(session)
        self.credit_repo = CreditRepository(session)
        self.payment_repo = PaymentRepository(session)
        self._document_service = DocumentService(session)
        self._portfolio_document_repo = PortfolioDocumentRepository(session)

    def _bulk_upsert_enabled(self) -> bool:
        """Misma env var que `PortfolioCsvService`, leída en cada llamada (no cacheada)
        para poder togglear el flag sin redeploy."""
        return (
            get_or_default(
                PORTFOLIO_CSV_BULK_UPSERT_ENV_VAR, DEFAULT_PORTFOLIO_CSV_BULK_UPSERT
            )
            == "true"
        )

    async def upload(
        self, portfolio_id: uuid.UUID, file_bytes: bytes, filename: str = ""
    ) -> InstallmentsUploadResult:
        logger.info(
            "[installment_csv] START | portfolio=%s bytes=%d",
            portfolio_id,
            len(file_bytes),
        )
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if portfolio is None:
            raise ValueError(f"Portafolio {portfolio_id} no encontrado")

        file_data = self.parser.parse(file_bytes, filename)
        logger.info(
            "[installment_csv] parsed | filas=%d skipped=%d",
            len(file_data.rows),
            file_data.total_skipped,
        )

        await self._archive_source_file(portfolio, file_bytes, filename)

        total_rows = len(file_data.rows) + file_data.total_skipped
        processed = 0
        cuotas_creadas = 0
        cuotas_actualizadas = 0
        creditos_liquidados = 0
        errors: list[str] = []

        # Precarga en 1 query los créditos que van a hacer falta, en vez de un SELECT
        # por fila (Fase 4 de la auditoría, mismo flag que portfolio_csv_service -- el
        # upsert de la cuota en sí queda por fila: PaymentModel no tiene un constraint
        # único que sirva de target para ON CONFLICT, y el camino de liquidación total
        # es lógica de negocio por-crédito que no vale la pena forzar a bulk).
        bulk_enabled = self._bulk_upsert_enabled()
        credit_by_number: dict[str, CreditModel] = {}
        if bulk_enabled:
            credit_numbers = list({row.credit_number for row in file_data.rows})
            credit_by_number = {
                c.credit_number: c
                for c in await self.credit_repo.get_by_credit_numbers(
                    credit_numbers, portfolio_id
                )
            }

        for idx, row in enumerate(file_data.rows, start=1):
            try:
                async with self.session.begin_nested():
                    credit = (
                        credit_by_number.get(row.credit_number)
                        if bulk_enabled
                        else await self.credit_repo.get_by_credit_number(
                            row.credit_number, portfolio_id
                        )
                    )
                    if credit is None:
                        raise ValueError(
                            f"El crédito {row.credit_number} no existe en este "
                            "portafolio"
                        )
                    if row.is_full_settlement:
                        await self._settle_credit(credit, row)
                        creditos_liquidados += 1
                    else:
                        created = await self._upsert_installment(credit.id, row)
                        if created:
                            cuotas_creadas += 1
                        else:
                            cuotas_actualizadas += 1
            except Exception as exc:
                logger.warning("[installment_csv] ERROR | fila=%d error=%s", idx, exc)
                if len(errors) < MAX_ERRORS:
                    errors.append(f"Fila {idx} (crédito {row.credit_number}): {exc}")
                continue
            processed += 1

        failed = len(file_data.rows) - processed
        result = InstallmentsUploadResult(
            total_rows=total_rows,
            processed_rows=processed,
            failed_rows=failed,
            portfolio_id=portfolio_id,
            cuotas_creadas=cuotas_creadas,
            cuotas_actualizadas=cuotas_actualizadas,
            creditos_liquidados=creditos_liquidados,
            errors=errors,
        )
        logger.info(
            "[installment_csv] END | procesados=%d fallidos=%d creadas=%d "
            "actualizadas=%d liquidados=%d",
            processed,
            failed,
            cuotas_creadas,
            cuotas_actualizadas,
            creditos_liquidados,
        )
        return result

    # ------------------------------------------------------------------
    # Row handlers
    # ------------------------------------------------------------------

    async def _upsert_installment(
        self, credit_id: uuid.UUID, row: InstallmentRowData
    ) -> bool:
        """Devuelve True si creó una cuota nueva, False si actualizó una existente."""
        assert (
            row.installment_number is not None
        )  # el parser ya lo garantiza para filas no-liquidación
        existing = await self.payment_repo.get_by_credit_and_installment(
            credit_id, row.installment_number
        )
        status = PaymentStatus.PAID if row.payment_date else PaymentStatus.PENDING

        if existing is not None:
            existing.limit_pay_date = row.limit_pay_date
            existing.payment_date = row.payment_date
            existing.payment_amount = row.payment_amount
            existing.principal_payment = row.principal_payment
            existing.current_interest_amount = row.current_interest_amount
            existing.overdue_interest_amount = row.overdue_interest_amount
            existing.life_insurance_charge = row.life_insurance_charge
            existing.vehicle_insurance_charge = row.vehicle_insurance_charge
            existing.insurances_total = (
                row.life_insurance_charge + row.vehicle_insurance_charge
            )
            existing.other_charges = row.other_charges
            existing.total_interest_amount = (
                row.current_interest_amount + row.overdue_interest_amount
            )
            existing.vat = row.vat
            existing.commission_amount = row.commission_amount
            existing.platform_fee = row.platform_fee
            existing.status = status
            await self.payment_repo.update(existing)
            return False

        await self.payment_repo.add(
            PaymentModel(
                credit_id=credit_id,
                installment_number=row.installment_number,
                limit_pay_date=row.limit_pay_date,
                payment_date=row.payment_date,
                payment_amount=row.payment_amount,
                principal_payment=row.principal_payment,
                current_interest_amount=row.current_interest_amount,
                overdue_interest_amount=row.overdue_interest_amount,
                life_insurance_charge=row.life_insurance_charge,
                vehicle_insurance_charge=row.vehicle_insurance_charge,
                insurances_total=row.life_insurance_charge
                + row.vehicle_insurance_charge,
                other_charges=row.other_charges,
                total_interest_amount=row.current_interest_amount
                + row.overdue_interest_amount,
                other_concepts_amount=0,
                vat=row.vat,
                commission_amount=row.commission_amount,
                platform_fee=row.platform_fee,
                condonation_amount=0,
                discount_amount=0,
                status=status,
            )
        )
        return True

    async def _settle_credit(
        self, credit: CreditModel, row: InstallmentRowData
    ) -> None:
        """Pago total del crédito: registra el pago, cierra (soft-delete) las cuotas
        pendientes que quedaban y desactiva el crédito — mismo criterio que
        CreditSettlementResolutionService usa para la autogestión del titular."""
        await self.payment_repo.add(
            PaymentModel(
                credit_id=credit.id,
                installment_number=None,
                limit_pay_date=row.limit_pay_date,
                payment_date=row.payment_date or datetime.now(timezone.utc),
                payment_amount=row.payment_amount,
                principal_payment=row.principal_payment,
                current_interest_amount=row.current_interest_amount,
                overdue_interest_amount=row.overdue_interest_amount,
                life_insurance_charge=row.life_insurance_charge,
                vehicle_insurance_charge=row.vehicle_insurance_charge,
                insurances_total=row.life_insurance_charge
                + row.vehicle_insurance_charge,
                other_charges=row.other_charges,
                total_interest_amount=row.current_interest_amount
                + row.overdue_interest_amount,
                other_concepts_amount=0,
                vat=row.vat,
                commission_amount=row.commission_amount,
                platform_fee=row.platform_fee,
                condonation_amount=0,
                discount_amount=0,
                status=PaymentStatus.PAID,
            )
        )

        pending = await self.payment_repo.get_pending_by_credit_id(credit.id)
        await self.payment_repo.delete_many(pending)

        credit.is_active = False
        await self.credit_repo.update(credit)

    async def _archive_source_file(
        self, portfolio: PortfolioModel, file_bytes: bytes, filename: str
    ):
        is_xlsx = filename.lower().endswith(".xlsx")
        ext = "xlsx" if is_xlsx else "csv"
        timestamp = int(datetime.now(timezone.utc).timestamp())
        document = await self._document_service.store_generated(
            content=file_bytes,
            filename=f"{portfolio.id}_installments_{timestamp}.{ext}",
            content_type=XLSX_CONTENT_TYPE if is_xlsx else CSV_CONTENT_TYPE,
            domain=PORTFOLIO_DOCUMENT_STORAGE_DOMAIN,
            owner_id=str(portfolio.id),
            organization_id=portfolio.organization_id,
        )
        # El enlace al portafolio es una fila propia con FK real, en la misma sesión.
        return await self._portfolio_document_repo.add(
            PortfolioDocumentModel(
                portfolio_id=portfolio.id,
                organization_id=portfolio.organization_id,
                category=PortfolioDocumentCategory.PORTFOLIO_SOURCE,
                document_id=document.id,
            )
        )
