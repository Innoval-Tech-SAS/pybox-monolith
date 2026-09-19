"""Parser del CSV/XLSX de plan de cuotas — carga independiente del importador grande de
portafolio (`portfolio_file_parser.py`). No comparte código con él a propósito: es un
archivo con columnas propias para una feature separada (ver
`PortfolioCsvService.upload_installments_csv`), no una variante del flujo existente.
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO
from typing import Any

import polars as pl

from receivables.portfolios.constants.portfolio_csv_constants import (
    AFFIRMATIVE_STRINGS,
    DATE_FORMATS,
    INSTALLMENT_REQUIRED_COLUMNS,
    NULL_STRINGS,
)
from receivables.portfolios.schemas.portfolio_file_schemas import InstallmentFileData, InstallmentRowData


class InstallmentFileParser:

    @staticmethod
    def _as_utf8(file_bytes: bytes) -> bytes:
        try:
            file_bytes.decode("utf-8")
            return file_bytes
        except UnicodeDecodeError:
            return file_bytes.decode("cp1252", errors="replace").encode("utf-8")

    def parse(self, file_bytes: bytes, filename: str = "") -> InstallmentFileData:
        if not file_bytes:
            raise ValueError("El archivo está vacío")

        is_xlsx = filename.lower().endswith(".xlsx") or file_bytes[:4] == b"PK\x03\x04"
        if is_xlsx:
            df = pl.read_excel(BytesIO(file_bytes))
            df = df.select([pl.col(c).cast(pl.String, strict=False) for c in df.columns])
        else:
            df = pl.read_csv(
                BytesIO(self._as_utf8(file_bytes)),
                infer_schema_length=0,
                ignore_errors=True,
                truncate_ragged_lines=True,
            )
        self._validate_columns(set(df.columns))

        rows: list[InstallmentRowData] = []
        total_skipped = 0

        for raw in df.to_dicts():
            row = self._build_row(raw)
            if row is None:
                total_skipped += 1
                continue
            rows.append(row)

        return InstallmentFileData(rows=rows, total_skipped=total_skipped)

    def _validate_columns(self, columns: set[str]) -> None:
        missing = INSTALLMENT_REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(
                f"El archivo no tiene las columnas requeridas: {', '.join(sorted(missing))}"
            )

    def _build_row(self, raw: dict[str, Any]) -> InstallmentRowData | None:
        credit_number = self._normalize_str(raw.get("Numero de credito"))
        if not credit_number:
            return None

        is_full_settlement = self._to_bool(raw.get("Pago total del credito"))
        installment_number = self._to_int_or_none(raw.get("Numero de la cuota que se cancela"))
        if not is_full_settlement and installment_number is None:
            return None

        limit_pay_date = self._parse_date(raw.get("Fecha limite de pago"))
        if limit_pay_date is None:
            return None

        return InstallmentRowData(
            credit_number=credit_number,
            installment_number=installment_number,
            is_full_settlement=is_full_settlement,
            limit_pay_date=limit_pay_date,
            payment_date=self._parse_date(raw.get("Fecha del pago")),
            payment_amount=self._to_decimal(raw.get("total")),
            principal_payment=self._to_decimal(raw.get("abono a capital")),
            current_interest_amount=self._to_decimal(raw.get("interes corriente")),
            overdue_interest_amount=self._to_decimal(raw.get("interes mora")),
            life_insurance_charge=self._to_decimal(raw.get("Seguro de vida")),
            vehicle_insurance_charge=self._to_decimal(raw.get("seguro de vehiculo")),
            other_charges=self._to_decimal(raw.get("otros cargos")),
            vat=self._to_decimal(raw.get("IVA")),
            commission_amount=self._to_decimal(raw.get("Comision")),
            platform_fee=self._to_decimal(raw.get("Plataforma")),
        )

    # ------------------------------------------------------------------
    # Normalizers
    # ------------------------------------------------------------------

    def _normalize_str(self, value: Any) -> str | None:
        if value is None:
            return None
        s = str(value).strip()
        if s.lower() in NULL_STRINGS:
            return None
        return s

    def _to_bool(self, value: Any) -> bool:
        s = self._normalize_str(value)
        if s is None:
            return False
        return s.strip().lower() in AFFIRMATIVE_STRINGS

    def _to_decimal(self, value: Any, default: Decimal = Decimal("0")) -> Decimal:
        result = self._to_decimal_or_none(value)
        return result if result is not None else default

    def _to_decimal_or_none(self, value: Any) -> Decimal | None:
        s = self._normalize_str(value)
        if s is None:
            return None
        try:
            return Decimal(s.replace(",", ""))
        except InvalidOperation:
            return None

    def _to_int_or_none(self, value: Any) -> int | None:
        s = self._normalize_str(value)
        if s is None:
            return None
        try:
            return int(Decimal(s.replace(",", "")))
        except (InvalidOperation, ValueError):
            return None

    def _parse_date(self, value: Any) -> datetime | None:
        s = self._normalize_str(value)
        if s is None:
            return None
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        return None
