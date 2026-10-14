"""Tests unitarios de `InstallmentFileParser` -- parseo del CSV/XLSX de plan de
cuotas. Sin DB ni HTTP: solo bytes -> `InstallmentFileData`.
"""

from datetime import datetime
from decimal import Decimal

import pytest

from receivables.portfolios.utils.installment_file_parser import InstallmentFileParser
from tests.receivables.conftest import build_installments_csv


def installment_row(**overrides) -> dict[str, str]:
    row = {
        "Numero de credito": "CR-0001",
        "Numero de la cuota que se cancela": "3",
        "Pago total del credito": "no",
        "Fecha limite de pago": "01/01/2026",
        "Fecha del pago": "05/01/2026",
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


class TestParseValidRows:
    def test_valid_row_is_parsed_with_correct_types(self):
        parser = InstallmentFileParser()
        data = parser.parse(build_installments_csv([installment_row()]))

        assert data.total_skipped == 0
        assert len(data.rows) == 1
        row = data.rows[0]
        assert row.credit_number == "CR-0001"
        assert row.installment_number == 3
        assert row.is_full_settlement is False
        assert row.limit_pay_date == datetime(2026, 1, 1)
        assert row.payment_date == datetime(2026, 1, 5)
        assert row.payment_amount == Decimal("150000")
        assert row.principal_payment == Decimal("100000")

    def test_full_settlement_row_allows_missing_installment_number(self):
        parser = InstallmentFileParser()
        data = parser.parse(
            build_installments_csv(
                [
                    installment_row(
                        **{
                            "Pago total del credito": "si",
                            "Numero de la cuota que se cancela": "",
                        }
                    )
                ]
            )
        )

        assert data.total_skipped == 0
        row = data.rows[0]
        assert row.is_full_settlement is True
        assert row.installment_number is None

    def test_pending_installment_has_no_payment_date(self):
        parser = InstallmentFileParser()
        data = parser.parse(
            build_installments_csv([installment_row(**{"Fecha del pago": ""})])
        )

        assert data.rows[0].payment_date is None


class TestParseSkipsInvalidRows:
    def test_missing_credit_number_is_skipped(self):
        parser = InstallmentFileParser()
        data = parser.parse(
            build_installments_csv([installment_row(**{"Numero de credito": ""})])
        )
        assert data.rows == []
        assert data.total_skipped == 1

    def test_missing_installment_number_without_full_settlement_is_skipped(self):
        parser = InstallmentFileParser()
        data = parser.parse(
            build_installments_csv(
                [
                    installment_row(
                        **{
                            "Numero de la cuota que se cancela": "",
                            "Pago total del credito": "no",
                        }
                    )
                ]
            )
        )
        assert data.rows == []
        assert data.total_skipped == 1

    def test_non_numeric_installment_number_is_skipped(self):
        # `_to_int_or_none` no puede convertir "abc" -> None -> misma regla que vacío.
        parser = InstallmentFileParser()
        data = parser.parse(
            build_installments_csv(
                [installment_row(**{"Numero de la cuota que se cancela": "abc"})]
            )
        )
        assert data.rows == []
        assert data.total_skipped == 1

    def test_missing_limit_pay_date_is_skipped(self):
        parser = InstallmentFileParser()
        data = parser.parse(
            build_installments_csv([installment_row(**{"Fecha limite de pago": ""})])
        )
        assert data.rows == []
        assert data.total_skipped == 1

    def test_unparseable_limit_pay_date_is_skipped(self):
        parser = InstallmentFileParser()
        data = parser.parse(
            build_installments_csv(
                [installment_row(**{"Fecha limite de pago": "not-a-date"})]
            )
        )
        assert data.rows == []
        assert data.total_skipped == 1


class TestParseNumericNormalization:
    def test_non_numeric_amount_falls_back_to_zero(self):
        parser = InstallmentFileParser()
        data = parser.parse(
            build_installments_csv([installment_row(**{"total": "no-es-un-numero"})])
        )
        assert data.rows[0].payment_amount == Decimal("0")

    def test_amount_with_thousands_comma_is_parsed(self):
        parser = InstallmentFileParser()
        data = parser.parse(
            build_installments_csv([installment_row(**{"total": "1,500,000"})])
        )
        assert data.rows[0].payment_amount == Decimal("1500000")


class TestParseColumnsAndEmptyFile:
    def test_empty_file_raises(self):
        parser = InstallmentFileParser()
        with pytest.raises(ValueError, match="vacío"):
            parser.parse(b"")

    def test_missing_required_column_raises(self):
        parser = InstallmentFileParser()
        with pytest.raises(ValueError, match="columnas requeridas"):
            parser.parse(b"Numero de credito\nCR-1\n")
