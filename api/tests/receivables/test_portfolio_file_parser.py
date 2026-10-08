"""Cierra gaps puntuales de `PortfolioFileParser` no cubiertos por
`test_portfolio_csv_upload.py` (que solo ejercita el camino feliz vía HTTP): fallback
de encoding, rama .xlsx real, filas sin codeudor completo, mapeo de tipos con alias
desconocidos, direccion secundaria opcional y los sub-registros opcionales (pago,
cotizacion UVR, ajuste de credito).
"""

import csv
import io

from app_platform.countries.enums.country_enums import UserDocumentType
from receivables.credits.enums.credit_enums import CreditTypes
from receivables.debtors.enums.debtor_enums import DebtorType
from receivables.portfolios.constants.portfolio_csv_constants import PORTFOLIO_TEMPLATE_COLUMNS
from receivables.portfolios.utils.portfolio_file_parser import PortfolioFileParser
from tests.receivables.conftest import build_minimal_xlsx, build_portfolio_csv, portfolio_csv_row


def build_portfolio_csv_cp1252(rows: list[dict[str, str]]) -> bytes:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=PORTFOLIO_TEMPLATE_COLUMNS)
    writer.writeheader()
    for row in rows:
        writer.writerow({col: row.get(col, "") for col in PORTFOLIO_TEMPLATE_COLUMNS})
    return buf.getvalue().encode("cp1252")


class TestEncodingFallback:
    def test_cp1252_bytes_fall_back_and_decode_accents(self):
        parser = PortfolioFileParser()
        csv_bytes = build_portfolio_csv_cp1252([portfolio_csv_row(**{"Nombre del titular": "Muñoz Peña"})])

        data = parser.parse(csv_bytes)

        assert len(data.rows) == 1
        assert data.rows[0].debtor.full_name == "Muñoz Peña"


class TestEmptyFile:
    def test_empty_bytes_raises(self):
        import pytest

        parser = PortfolioFileParser()
        with pytest.raises(ValueError, match="vacío"):
            parser.parse(b"")


class TestXlsxBranch:
    def test_parses_a_real_xlsx_file(self):
        row = portfolio_csv_row(**{"Nombre del titular": "Titular XLSX"})
        xlsx_bytes = build_minimal_xlsx(
            PORTFOLIO_TEMPLATE_COLUMNS,
            [[row.get(col, "") for col in PORTFOLIO_TEMPLATE_COLUMNS]],
        )

        parser = PortfolioFileParser()
        data = parser.parse(xlsx_bytes, filename="cartera.xlsx")

        assert len(data.rows) == 1
        assert data.rows[0].debtor.full_name == "Titular XLSX"

    def test_detects_xlsx_by_magic_bytes_even_without_extension(self):
        row = portfolio_csv_row()
        xlsx_bytes = build_minimal_xlsx(
            PORTFOLIO_TEMPLATE_COLUMNS,
            [[row.get(col, "") for col in PORTFOLIO_TEMPLATE_COLUMNS]],
        )

        parser = PortfolioFileParser()
        data = parser.parse(xlsx_bytes, filename="")  # sin .xlsx: se detecta por PK\x03\x04

        assert len(data.rows) == 1


class TestSkipsIncompleteRows:
    def test_row_without_document_number_is_skipped(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([portfolio_csv_row(**{"Numero de documento": ""})]))
        assert data.rows == []
        assert data.total_skipped == 1

    def test_row_without_credit_number_is_skipped(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([portfolio_csv_row(**{"Numero de credito": ""})]))
        assert data.rows == []
        assert data.total_skipped == 1


class TestCodebtor:
    def test_codebtor_name_without_document_is_ignored(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([
            portfolio_csv_row(**{"Nombre del Codeudor": "Codeudor sin doc", "Numero de documento codeudor": ""})
        ]))
        assert data.rows[0].codebtor is None

    def test_codebtor_with_name_and_document_is_built(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([
            portfolio_csv_row(**{
                "Nombre del Codeudor": "Codeudor Completo",
                "Numero de documento codeudor": "900123456",
            })
        ]))
        codebtor = data.rows[0].codebtor
        assert codebtor is not None
        assert codebtor.full_name == "Codeudor Completo"
        assert codebtor.document_number == "900123456"
        assert codebtor.debtor_type == DebtorType.CO_DEBTOR

    def test_no_codebtor_name_means_no_codebtor(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([portfolio_csv_row()]))
        assert data.rows[0].codebtor is None


class TestSecondaryAddress:
    def test_missing_second_city_means_no_secondary_address(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([portfolio_csv_row()]))
        assert data.rows[0].secondary_address is None

    def test_second_city_present_builds_secondary_address(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([
            portfolio_csv_row(**{"Ciudad 2": "Medellin", "Direccion 2": "Calle 2", "Departamento 2": "Antioquia"})
        ]))
        secondary = data.rows[0].secondary_address
        assert secondary is not None
        assert secondary.city == "Medellin"
        assert secondary.address_type == "SECONDARY"


class TestDocumentTypeMapping:
    def test_unknown_document_type_code_defaults_to_cc(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([portfolio_csv_row(**{"Tipo documento": "CODIGO-INVENTADO"})]))
        assert data.rows[0].debtor.document_type == UserDocumentType.CC

    def test_known_document_type_code_is_mapped(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([portfolio_csv_row(**{"Tipo documento": "CE"})]))
        assert data.rows[0].debtor.document_type == UserDocumentType.CE


class TestCreditTypeMapping:
    def test_unknown_credit_type_alias_defaults_to_other_service(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([portfolio_csv_row(**{"Tipo de producto": "PRODUCTO-RARO"})]))
        assert data.rows[0].credit.credit_type == CreditTypes.OTHER_SERVICE

    def test_known_alias_is_mapped(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([portfolio_csv_row(**{"Tipo de producto": "TC"})]))
        assert data.rows[0].credit.credit_type == CreditTypes.CREDIT_CARD


class TestOptionalPayment:
    def test_no_payment_date_means_no_payment(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([portfolio_csv_row()]))
        assert data.rows[0].payment is None

    def test_payment_date_without_limit_date_falls_back_to_payment_date(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([
            portfolio_csv_row(**{"Fecha del pago": "10/01/2026", "Fecha limite de pago": "", "total": "50000"})
        ]))
        payment = data.rows[0].payment
        assert payment is not None
        assert payment.limit_pay_date == payment.payment_date


class TestOptionalUVRQuote:
    def test_missing_quote_value_means_no_uvr_quote(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([portfolio_csv_row()]))
        assert data.rows[0].uvr_quote is None

    def test_quote_value_without_court_date_means_no_uvr_quote(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([
            portfolio_csv_row(**{"Cotizacion de UVR": "350.55", "Fecha de corte": ""})
        ]))
        assert data.rows[0].uvr_quote is None

    def test_quote_value_and_court_date_build_uvr_quote(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([
            portfolio_csv_row(**{"Cotizacion de UVR": "350.55", "Fecha de corte": "01/02/2026"})
        ]))
        quote = data.rows[0].uvr_quote
        assert quote is not None
        assert str(quote.quote_value) == "350.55"


class TestOptionalCreditAdjustment:
    def test_missing_amount_means_no_adjustment(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([portfolio_csv_row()]))
        assert data.rows[0].credit_adjustment is None

    def test_amount_without_cutoff_date_falls_back_to_now(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([
            portfolio_csv_row(**{"Condonaciones y/o descuentos": "1000", "Fecha de corte": ""})
        ]))
        adjustment = data.rows[0].credit_adjustment
        assert adjustment is not None
        assert adjustment.applied_date is not None

    def test_amount_with_cutoff_date_uses_it(self):
        parser = PortfolioFileParser()
        data = parser.parse(build_portfolio_csv([
            portfolio_csv_row(**{"Condonaciones y/o descuentos": "1000", "Fecha de corte": "01/02/2026"})
        ]))
        adjustment = data.rows[0].credit_adjustment
        assert adjustment.applied_date.day == 1
        assert adjustment.applied_date.month == 2
