"""Tests de `InstallmentCsvService.upload()` contra la base de datos real
(`db_session`, sin mocks): cuotas creadas vs. actualizadas, liquidación de crédito
cuando llega una fila de pago total, y créditos no encontrados en el portafolio.
"""

import uuid
from datetime import datetime, timezone

import pytest

from receivables.credits.repository.credit_repository import CreditRepository
from receivables.payments.enums.payment_enums import PaymentStatus
from receivables.payments.models.payment_model import PaymentModel
from receivables.payments.repository.payment_repository import PaymentRepository
from receivables.portfolios.services.installment_csv_service import InstallmentCsvService
from tests.receivables.conftest import build_credit, build_debtor, build_organization, build_portfolio, build_installments_csv


def installment_row(**overrides) -> dict[str, str]:
    row = {
        "Numero de credito": "CR-0001",
        "Numero de la cuota que se cancela": "1",
        "Pago total del credito": "no",
        "Fecha limite de pago": "01/01/2026",
        "Fecha del pago": "",
        "total": "150000",
        "abono a capital": "100000",
        "interes corriente": "30000",
        "interes mora": "0",
        "Seguro de vida": "5000",
        "seguro de vehiculo": "0",
        "otros cargos": "0",
        "IVA": "0",
        "Comision": "0",
        "Plataforma": "0",
    }
    row.update(overrides)
    return row


@pytest.fixture
async def portfolio_with_credit(db_session):
    org = build_organization()
    db_session.add(org)
    await db_session.flush()
    portfolio = build_portfolio(org.id)
    db_session.add(portfolio)
    await db_session.flush()
    debtor = build_debtor(org.id)
    db_session.add(debtor)
    await db_session.flush()
    credit = build_credit(portfolio.id, debtor.id, credit_number="CR-0001")
    db_session.add(credit)
    await db_session.flush()
    return portfolio, credit


class TestUploadCreatesAndUpdatesInstallments:
    async def test_new_installment_number_creates_a_payment(self, db_session, portfolio_with_credit):
        portfolio, credit = portfolio_with_credit
        service = InstallmentCsvService(db_session)
        csv_bytes = build_installments_csv([installment_row()])

        result = await service.upload(portfolio.id, csv_bytes, "cuotas.csv")

        assert result.processed_rows == 1
        assert result.failed_rows == 0
        assert result.cuotas_creadas == 1
        assert result.cuotas_actualizadas == 0
        assert result.creditos_liquidados == 0

        payment_repo = PaymentRepository(db_session)
        payment = await payment_repo.get_by_credit_and_installment(credit.id, 1)
        assert payment is not None
        assert payment.payment_amount == 150000
        assert payment.status == PaymentStatus.PENDING

    async def test_existing_installment_number_updates_the_payment(self, db_session, portfolio_with_credit):
        portfolio, credit = portfolio_with_credit
        service = InstallmentCsvService(db_session)
        await service.upload(portfolio.id, build_installments_csv([installment_row()]), "cuotas.csv")

        result = await service.upload(
            portfolio.id,
            build_installments_csv([installment_row(**{"total": "200000", "Fecha del pago": "10/01/2026"})]),
            "cuotas2.csv",
        )

        assert result.cuotas_creadas == 0
        assert result.cuotas_actualizadas == 1

        payment_repo = PaymentRepository(db_session)
        payment = await payment_repo.get_by_credit_and_installment(credit.id, 1)
        assert payment.payment_amount == 200000
        assert payment.status == PaymentStatus.PAID  # trae fecha de pago -> PAID


class TestUploadFullSettlement:
    async def test_settles_credit_and_closes_pending_installments(self, db_session, portfolio_with_credit):
        portfolio, credit = portfolio_with_credit
        payment_repo = PaymentRepository(db_session)
        pending = await payment_repo.add(
            PaymentModel(
                credit_id=credit.id,
                installment_number=2,
                limit_pay_date=datetime.now(timezone.utc),
                payment_date=None,
                status=PaymentStatus.PENDING,
            )
        )

        service = InstallmentCsvService(db_session)
        csv_bytes = build_installments_csv([
            installment_row(**{"Pago total del credito": "si", "Numero de la cuota que se cancela": ""})
        ])
        result = await service.upload(portfolio.id, csv_bytes, "cuotas.csv")

        assert result.creditos_liquidados == 1
        assert result.processed_rows == 1

        await db_session.refresh(credit)
        assert credit.is_active is False

        await db_session.refresh(pending)
        assert pending.deleted_at is not None


class TestUploadErrors:
    async def test_portfolio_not_found_raises(self, db_session):
        service = InstallmentCsvService(db_session)
        with pytest.raises(ValueError, match="no encontrado"):
            await service.upload(uuid.uuid4(), build_installments_csv([installment_row()]), "cuotas.csv")

    async def test_unknown_credit_number_is_reported_as_error_row(self, db_session, portfolio_with_credit):
        portfolio, _credit = portfolio_with_credit
        service = InstallmentCsvService(db_session)
        csv_bytes = build_installments_csv([installment_row(**{"Numero de credito": "NO-EXISTE"})])

        result = await service.upload(portfolio.id, csv_bytes, "cuotas.csv")

        assert result.processed_rows == 0
        assert result.failed_rows == 1
        assert len(result.errors) == 1
        assert "NO-EXISTE" in result.errors[0]

    async def test_credit_in_different_portfolio_is_reported_as_error_row(self, db_session, portfolio_with_credit):
        _portfolio, credit = portfolio_with_credit
        other_org = build_organization()
        db_session.add(other_org)
        await db_session.flush()
        other_portfolio = build_portfolio(other_org.id)
        db_session.add(other_portfolio)
        await db_session.flush()

        service = InstallmentCsvService(db_session)
        csv_bytes = build_installments_csv([installment_row(**{"Numero de credito": credit.credit_number})])

        result = await service.upload(other_portfolio.id, csv_bytes, "cuotas.csv")

        assert result.processed_rows == 0
        assert result.failed_rows == 1


class TestUploadCharacterizationGolden:
    """Congela el comportamiento ACTUAL de `upload` (savepoint por fila, un solo
    `for` sin precarga) ANTES del refactor de precarga + bulk-upsert planeado en la
    auditoría (Fase 4). Un solo archivo con los 4 caminos que existen hoy: cuota
    nueva (insert), cuota existente (update), liquidación total de crédito, y una
    fila inválida (crédito inexistente) en medio de las válidas -- para confirmar
    que el aislamiento por SAVEPOINT deja procesar las filas posteriores."""

    async def test_mixed_batch_preserves_row_isolation(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        debtor = build_debtor(org.id)
        db_session.add(debtor)
        await db_session.flush()

        credit_update = build_credit(portfolio.id, debtor.id, credit_number="CR-GOLDEN-UPDATE")
        credit_insert = build_credit(portfolio.id, debtor.id, credit_number="CR-GOLDEN-INSERT")
        credit_settle = build_credit(portfolio.id, debtor.id, credit_number="CR-GOLDEN-SETTLE")
        db_session.add_all([credit_update, credit_insert, credit_settle])
        await db_session.flush()

        payment_repo = PaymentRepository(db_session)
        pending_to_update = await payment_repo.add(
            PaymentModel(
                credit_id=credit_update.id,
                installment_number=2,
                limit_pay_date=datetime.now(timezone.utc),
                payment_date=None,
                status=PaymentStatus.PENDING,
            )
        )
        pending_to_close_on_settle = await payment_repo.add(
            PaymentModel(
                credit_id=credit_settle.id,
                installment_number=1,
                limit_pay_date=datetime.now(timezone.utc),
                payment_date=None,
                status=PaymentStatus.PENDING,
            )
        )

        rows = [
            installment_row(**{
                "Numero de credito": "CR-GOLDEN-UPDATE",
                "Numero de la cuota que se cancela": "2",
                "total": "999999",
                "Fecha del pago": "05/01/2026",
            }),
            installment_row(**{
                "Numero de credito": "CR-GOLDEN-INSERT",
                "Numero de la cuota que se cancela": "1",
            }),
            installment_row(**{"Numero de credito": "NO-EXISTE-GOLDEN"}),
            installment_row(**{
                "Numero de credito": "CR-GOLDEN-SETTLE",
                "Pago total del credito": "si",
                "Numero de la cuota que se cancela": "",
            }),
        ]

        service = InstallmentCsvService(db_session)
        result = await service.upload(portfolio.id, build_installments_csv(rows), "cuotas-golden.csv")

        # --- Golden congelado: comparar campo a campo tras el refactor de la Fase 4. ---
        assert result.total_rows == 4
        assert result.processed_rows == 3
        assert result.failed_rows == 1
        assert result.cuotas_creadas == 1
        assert result.cuotas_actualizadas == 1
        assert result.creditos_liquidados == 1
        assert len(result.errors) == 1
        assert "NO-EXISTE-GOLDEN" in result.errors[0]

        # Update: misma cuota (id), datos nuevos, no una segunda fila.
        await db_session.refresh(pending_to_update)
        assert pending_to_update.payment_amount == 999999
        assert pending_to_update.status == PaymentStatus.PAID

        # Insert: cuota nueva para el crédito que no tenía ninguna.
        insert_payment = await payment_repo.get_by_credit_and_installment(credit_insert.id, 1)
        assert insert_payment is not None

        # Settle: crédito desactivado y su cuota pendiente distinta a la liquidada
        # queda cerrada (soft-delete), aunque la fila inválida se procesó justo antes.
        await db_session.refresh(credit_settle)
        assert credit_settle.is_active is False
        await db_session.refresh(pending_to_close_on_settle)
        assert pending_to_close_on_settle.deleted_at is not None

        # La fila inválida no debe haber tocado nada del crédito CR-GOLDEN-UPDATE
        # procesado justo antes de ella (aislamiento por SAVEPOINT).
        credit_repo = CreditRepository(db_session)
        untouched = await credit_repo.get_by_credit_number("CR-GOLDEN-UPDATE", portfolio.id)
        assert untouched.is_active is True

    async def test_mixed_batch_matches_with_bulk_credit_preload(self, db_session, monkeypatch):
        """Mismo escenario que arriba, con `PORTFOLIO_CSV_BULK_UPSERT=true` (Fase 4):
        la precarga de créditos en 1 query no debe cambiar ningún resultado."""
        monkeypatch.setenv("PORTFOLIO_CSV_BULK_UPSERT", "true")

        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        debtor = build_debtor(org.id)
        db_session.add(debtor)
        await db_session.flush()

        credit_update = build_credit(portfolio.id, debtor.id, credit_number="CR-BULKGOLDEN-UPDATE")
        credit_insert = build_credit(portfolio.id, debtor.id, credit_number="CR-BULKGOLDEN-INSERT")
        credit_settle = build_credit(portfolio.id, debtor.id, credit_number="CR-BULKGOLDEN-SETTLE")
        db_session.add_all([credit_update, credit_insert, credit_settle])
        await db_session.flush()

        payment_repo = PaymentRepository(db_session)
        pending_to_update = await payment_repo.add(
            PaymentModel(
                credit_id=credit_update.id,
                installment_number=2,
                limit_pay_date=datetime.now(timezone.utc),
                payment_date=None,
                status=PaymentStatus.PENDING,
            )
        )
        pending_to_close_on_settle = await payment_repo.add(
            PaymentModel(
                credit_id=credit_settle.id,
                installment_number=1,
                limit_pay_date=datetime.now(timezone.utc),
                payment_date=None,
                status=PaymentStatus.PENDING,
            )
        )

        rows = [
            installment_row(**{
                "Numero de credito": "CR-BULKGOLDEN-UPDATE",
                "Numero de la cuota que se cancela": "2",
                "total": "999999",
                "Fecha del pago": "05/01/2026",
            }),
            installment_row(**{
                "Numero de credito": "CR-BULKGOLDEN-INSERT",
                "Numero de la cuota que se cancela": "1",
            }),
            installment_row(**{"Numero de credito": "NO-EXISTE-BULKGOLDEN"}),
            installment_row(**{
                "Numero de credito": "CR-BULKGOLDEN-SETTLE",
                "Pago total del credito": "si",
                "Numero de la cuota que se cancela": "",
            }),
        ]

        service = InstallmentCsvService(db_session)
        result = await service.upload(portfolio.id, build_installments_csv(rows), "cuotas-bulk-golden.csv")

        assert result.total_rows == 4
        assert result.processed_rows == 3
        assert result.failed_rows == 1
        assert result.cuotas_creadas == 1
        assert result.cuotas_actualizadas == 1
        assert result.creditos_liquidados == 1
        assert len(result.errors) == 1
        assert "NO-EXISTE-BULKGOLDEN" in result.errors[0]

        await db_session.refresh(pending_to_update)
        assert pending_to_update.payment_amount == 999999
        assert pending_to_update.status == PaymentStatus.PAID

        insert_payment = await payment_repo.get_by_credit_and_installment(credit_insert.id, 1)
        assert insert_payment is not None

        await db_session.refresh(credit_settle)
        assert credit_settle.is_active is False
        await db_session.refresh(pending_to_close_on_settle)
        assert pending_to_close_on_settle.deleted_at is not None

        credit_repo = CreditRepository(db_session)
        untouched = await credit_repo.get_by_credit_number("CR-BULKGOLDEN-UPDATE", portfolio.id)
        assert untouched.is_active is True
