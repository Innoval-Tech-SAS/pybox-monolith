"""`build_statement_pdf` no expone un parser de PDF en el repo -- el contrato que se
puede verificar sin dependencias nuevas es: no revienta con datos mínimos/vacíos, y
produce bytes con la cabecera `%PDF` real (reportlab). Los montos formateados en texto
se prueban aparte contra los helpers internos `_money`/`_date`, que sí son inspeccionables."""

from datetime import datetime, timezone

from receivables.statements.utils.statement_pdf_builder import (
    StatementCreditLine,
    StatementPaymentLine,
    _date,
    _money,
    build_statement_pdf,
)


def _credit_line(**overrides) -> StatementCreditLine:
    defaults = dict(
        credit_number="CR-0001",
        credit_type_label="Consumo",
        disbursed_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        total_credit_balance=1_000_000.5,
        overdue_principal_balance=50_000.25,
        days_overdue_at_cutoff=15,
        pending_installments=6,
        overdue_installments=1,
        payments=[],
    )
    defaults.update(overrides)
    return StatementCreditLine(**defaults)


def _payment_line(**overrides) -> StatementPaymentLine:
    defaults = dict(
        installment_number=1,
        limit_pay_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        payment_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        payment_amount=100_000.0,
        principal_payment=80_000.0,
        total_interest_amount=20_000.0,
        status_label="Pagada",
    )
    defaults.update(overrides)
    return StatementPaymentLine(**defaults)


class TestBuildStatementPdf:
    def test_no_credits_does_not_crash_and_returns_pdf_bytes(self):
        pdf = build_statement_pdf(
            organization_name="Acme",
            debtor_name="Ana Test",
            debtor_document="123456789",
            currency_code="COP",
            cutoff_date=datetime.now(timezone.utc),
            credits=[],
        )
        assert isinstance(pdf, bytes)
        assert pdf.startswith(b"%PDF")

    def test_single_credit_without_payments(self):
        pdf = build_statement_pdf(
            organization_name="Acme",
            debtor_name="Ana Test",
            debtor_document="123456789",
            currency_code="COP",
            cutoff_date=datetime.now(timezone.utc),
            credits=[_credit_line(payments=[])],
        )
        assert pdf.startswith(b"%PDF")
        assert len(pdf) > 100

    def test_multiple_credits_with_payments(self):
        pdf = build_statement_pdf(
            organization_name="Acme",
            debtor_name="Ana Test",
            debtor_document="123456789",
            currency_code="COP",
            cutoff_date=datetime.now(timezone.utc),
            credits=[
                _credit_line(credit_number="CR-0001", payments=[_payment_line()]),
                _credit_line(credit_number="CR-0002", payments=[_payment_line(), _payment_line(installment_number=2)]),
            ],
        )
        assert pdf.startswith(b"%PDF")

    def test_payment_with_no_payment_date_or_installment_number(self):
        """Cuota vencida sin pagar: `payment_date` e `installment_number` en None --
        no debe explotar el formateo (`_date`/str) en la tabla de pagos."""
        pdf = build_statement_pdf(
            organization_name="Acme",
            debtor_name="Ana Test",
            debtor_document="123456789",
            currency_code="COP",
            cutoff_date=datetime.now(timezone.utc),
            credits=[
                _credit_line(
                    payments=[_payment_line(installment_number=None, payment_date=None, status_label="Vencida")]
                )
            ],
        )
        assert pdf.startswith(b"%PDF")


class TestFormattingHelpers:
    def test_money_formats_with_thousands_separator_and_two_decimals(self):
        assert _money(1_234_567.5, "COP") == "COP 1,234,567.50"

    def test_money_zero(self):
        assert _money(0, "USD") == "USD 0.00"

    def test_date_formats_as_dd_mm_yyyy(self):
        assert _date(datetime(2026, 3, 4, tzinfo=timezone.utc)) == "04/03/2026"

    def test_date_none_returns_dash(self):
        assert _date(None) == "-"
