from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO
from typing import Any

import polars as pl

from receivables.contact_methods.enums.contact_method_enums import ContactMethodType
from platform.countries.enums.country_enums import UserDocumentType
from receivables.credits.enums.credit_enums import CreditTypes
from receivables.debtors.enums.debtor_enums import DebtorType

_NULL_STRINGS = {"n/a", "null", "sin dato", "none", ""}

_DOCUMENT_TYPE_MAP: dict[str, UserDocumentType] = {
    dt.value: dt for dt in UserDocumentType
}

_CREDIT_TYPE_MAP: dict[str, CreditTypes] = {
    "FINANCIAL_ENTITY": CreditTypes.FINANCIAL_ENTITY,
    "ENTIDAD FINANCIERA": CreditTypes.FINANCIAL_ENTITY,
    "FINTECH": CreditTypes.FINTECH,
    "SERVICES": CreditTypes.SERVICES,
    "SERVICIOS": CreditTypes.SERVICES,
    "PRODUCTS": CreditTypes.PRODUCTS,
    "PRODUCTOS": CreditTypes.PRODUCTS,
    "FASHION": CreditTypes.FASHION,
    "MODA": CreditTypes.FASHION,
    "RETAIL": CreditTypes.RETAIL,
    "PYMES": CreditTypes.PYMES,
    "OTHERS": CreditTypes.OTHERS,
    "OTROS": CreditTypes.OTHERS,
}

_DATE_FORMATS = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"]


@dataclass(frozen=True)
class DebtorRowData:
    document_number: str
    full_name: str
    document_type: UserDocumentType
    debtor_type: DebtorType


@dataclass(frozen=True)
class AddressRowData:
    address: str
    city: str
    state: str
    country: str
    address_type: str


@dataclass(frozen=True)
class ContactMethodRowData:
    contact_type: ContactMethodType
    contact_value: str


@dataclass(frozen=True)
class CreditRowData:
    credit_number: str
    credit_date: datetime | None
    disbursed_date: datetime | None
    credit_type: CreditTypes
    agreed_interest_rate: Decimal
    charged_effective_annual_rate: Decimal | None
    balance_disbursed: Decimal
    court_date: datetime | None
    initial_term: int
    total_credit_balance: Decimal
    overdue_principal_balance: Decimal
    current_interest: Decimal
    overdue_interest: Decimal
    other_concepts: Decimal
    overdue_installments: int
    days_overdue_at_cutoff: int
    amortization_system: str | None
    pending_installments: int
    insurance_total: Decimal
    commission_accum: Decimal
    platform_fee_accum: Decimal
    vat_accum: Decimal
    subproduct: str | None
    uvr_last_quote: Decimal | None
    condonations_accum: Decimal


@dataclass(frozen=True)
class PaymentRowData:
    payment_date: datetime
    limit_pay_date: datetime
    payment_amount: Decimal
    installment_number: int | None
    principal_payment: Decimal
    current_interest_amount: Decimal
    overdue_interest_amount: Decimal
    life_insurance_charge: Decimal
    vehicle_insurance_charge: Decimal
    other_charges: Decimal
    vat: Decimal
    commission_amount: Decimal
    platform_fee: Decimal


@dataclass(frozen=True)
class UVRQuoteRowData:
    quote_value: Decimal
    quote_date: datetime


@dataclass(frozen=True)
class CreditAdjustmentRowData:
    adjustment_amount: Decimal
    applied_date: datetime
    adjustment_type: str = "CONDONACION"


@dataclass(frozen=True)
class PortfolioRowData:
    debtor: DebtorRowData
    codebtor: DebtorRowData | None
    primary_address: AddressRowData
    secondary_address: AddressRowData | None
    debtor_contacts: list[ContactMethodRowData]
    codebtor_contacts: list[ContactMethodRowData]
    credit: CreditRowData
    payment: PaymentRowData | None
    uvr_quote: UVRQuoteRowData | None
    credit_adjustment: CreditAdjustmentRowData | None


@dataclass(frozen=True)
class PortfolioFileData:
    rows: list[PortfolioRowData]
    total_skipped: int


class PortfolioFileParser:
    REQUIRED_COLUMNS = {
        "Numero de documento",
        "Nombre del titular",
        "Tipo documento",
        "Telefono",
        "Correo Electronico",
        "Nombre del Codeudor",
        "Numero de documento codeudor",
        "Telefono codeudor",
        "Correo Electronico codeudor",
        "Ciudad",
        "Departamento",
        "Direccion",
        "Ciudad 2",
        "Departamento 2",
        "Direccion 2",
        "Numero de credito",
        "Fecha Desembolso",
        "Tipo de producto",
        "Tasa de interes pactada",
        "Tasa de interes cobrada",
        "Saldo Desembolso",
        "Fecha de corte",
        "plazo inicial",
        "saldo total del credito",
        "Saldo Capital en mora",
        "Intereses Corrientes",
        "Intereses Mora",
        "Otros Conceptos",
        "Cuotas en mora",
        "Dias en mora al corte",
        "Sistema de amortizacion",
        "numero de cuotas pendientes",
        "Seguros",
        "Comision",
        "Plataforma",
        "IVA",
        "SUBPRODUCTO",
        "Cotizacion de UVR",
        "Condonaciones y/o descuentos",
        "Fecha del pago",
        "Fecha limite de pago",
        "total",
        "Numero de la cuota que se cancela",
        "abono a capital",
        "interes corriente",
        "interes mora",
        "Seguro de vida",
        "seguro de vehiculo",
        "otros cargos",
    }

    def parse(self, file_bytes: bytes, filename: str = "") -> PortfolioFileData:
        if not file_bytes:
            raise ValueError("El archivo está vacío")

        is_xlsx = filename.lower().endswith(".xlsx") or file_bytes[:4] == b"PK\x03\x04"
        if is_xlsx:
            df = pl.read_excel(BytesIO(file_bytes))
            df = df.select([pl.col(c).cast(pl.String, strict=False) for c in df.columns])
        else:
            df = pl.read_csv(
                BytesIO(file_bytes),
                infer_schema_length=0,  # all columns as strings to avoid type coercion
                ignore_errors=True,
                truncate_ragged_lines=True,
            )
        self._validate_columns(set(df.columns))

        rows: list[PortfolioRowData] = []
        total_skipped = 0

        for raw in df.to_dicts():
            row = self._build_row(raw)
            if row is None:
                total_skipped += 1
                continue
            rows.append(row)

        return PortfolioFileData(rows=rows, total_skipped=total_skipped)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_columns(self, columns: set[str]) -> None:
        missing = self.REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(
                f"El archivo no tiene las columnas requeridas: {', '.join(sorted(missing))}"
            )

    # ------------------------------------------------------------------
    # Row builder — returns None to signal skip
    # ------------------------------------------------------------------

    def _build_row(self, raw: dict[str, Any]) -> PortfolioRowData | None:
        document_number = self._normalize_str(raw.get("Numero de documento"))
        credit_number = self._normalize_str(raw.get("Numero de credito"))

        if not document_number or not credit_number:
            return None

        debtor = self._build_debtor(raw, document_number)
        codebtor = self._build_codebtor(raw)
        primary_address = self._build_address(raw, "PRIMARY")
        secondary_address = self._build_secondary_address(raw)
        debtor_contacts = self._build_contacts(
            raw, "Telefono", "Correo Electronico"
        )
        codebtor_contacts = (
            self._build_contacts(raw, "Telefono codeudor", "Correo Electronico codeudor")
            if codebtor
            else []
        )
        credit = self._build_credit(raw, credit_number)
        payment = self._build_payment(raw)
        uvr_quote = self._build_uvr_quote(raw)
        credit_adjustment = self._build_credit_adjustment(raw)

        return PortfolioRowData(
            debtor=debtor,
            codebtor=codebtor,
            primary_address=primary_address,
            secondary_address=secondary_address,
            debtor_contacts=debtor_contacts,
            codebtor_contacts=codebtor_contacts,
            credit=credit,
            payment=payment,
            uvr_quote=uvr_quote,
            credit_adjustment=credit_adjustment,
        )

    # ------------------------------------------------------------------
    # Entity builders
    # ------------------------------------------------------------------

    def _build_debtor(self, raw: dict[str, Any], document_number: str) -> DebtorRowData:
        return DebtorRowData(
            document_number=document_number,
            full_name=self._normalize_str(raw.get("Nombre del titular")) or "",
            document_type=self._map_document_type(raw.get("Tipo documento")),
            debtor_type=DebtorType.DEBTOR,
        )

    def _build_codebtor(self, raw: dict[str, Any]) -> DebtorRowData | None:
        name = self._normalize_str(raw.get("Nombre del Codeudor"))
        if not name:
            return None
        doc_number = self._normalize_str(raw.get("Numero de documento codeudor"))
        if not doc_number:
            return None
        return DebtorRowData(
            document_number=doc_number,
            full_name=name,
            document_type=UserDocumentType.CC,
            debtor_type=DebtorType.CO_DEBTOR,
        )

    def _build_address(self, raw: dict[str, Any], address_type: str) -> AddressRowData:
        if address_type == "PRIMARY":
            return AddressRowData(
                address=self._normalize_str(raw.get("Direccion")) or "",
                city=self._normalize_str(raw.get("Ciudad")) or "",
                state=self._normalize_str(raw.get("Departamento")) or "",
                country="Colombia",
                address_type="PRIMARY",
            )
        return AddressRowData(
            address=self._normalize_str(raw.get("Direccion 2")) or "",
            city=self._normalize_str(raw.get("Ciudad 2")) or "",
            state=self._normalize_str(raw.get("Departamento 2")) or "",
            country="Colombia",
            address_type="SECONDARY",
        )

    def _build_secondary_address(self, raw: dict[str, Any]) -> AddressRowData | None:
        city2 = self._normalize_str(raw.get("Ciudad 2"))
        if not city2:
            return None
        return self._build_address(raw, "SECONDARY")

    def _build_contacts(
        self,
        raw: dict[str, Any],
        phone_col: str,
        email_col: str,
    ) -> list[ContactMethodRowData]:
        contacts: list[ContactMethodRowData] = []
        phone = self._normalize_phone(raw.get(phone_col))
        email = self._normalize_str(raw.get(email_col))
        if phone:
            contacts.append(ContactMethodRowData(ContactMethodType.PHONE, phone))
        if email:
            contacts.append(ContactMethodRowData(ContactMethodType.EMAIL, email))
        return contacts

    def _build_credit(self, raw: dict[str, Any], credit_number: str) -> CreditRowData:
        disbursed_date = self._parse_date(raw.get("Fecha Desembolso"))
        court_date = self._parse_date(raw.get("Fecha de corte"))
        return CreditRowData(
            credit_number=credit_number,
            credit_date=disbursed_date,
            disbursed_date=disbursed_date,
            credit_type=self._map_credit_type(raw.get("Tipo de producto")),
            agreed_interest_rate=self._to_decimal(raw.get("Tasa de interes pactada")),
            charged_effective_annual_rate=self._to_decimal_or_none(raw.get("Tasa de interes cobrada")),
            balance_disbursed=self._to_decimal(raw.get("Saldo Desembolso")),
            court_date=court_date,
            initial_term=self._to_int(raw.get("plazo inicial")),
            total_credit_balance=self._to_decimal(raw.get("saldo total del credito")),
            overdue_principal_balance=self._to_decimal(raw.get("Saldo Capital en mora")),
            current_interest=self._to_decimal(raw.get("Intereses Corrientes")),
            overdue_interest=self._to_decimal(raw.get("Intereses Mora")),
            other_concepts=self._to_decimal(raw.get("Otros Conceptos")),
            overdue_installments=self._to_int(raw.get("Cuotas en mora")),
            days_overdue_at_cutoff=self._to_int(raw.get("Dias en mora al corte")),
            amortization_system=self._normalize_str(raw.get("Sistema de amortizacion")),
            pending_installments=self._to_int(raw.get("numero de cuotas pendientes")),
            insurance_total=self._to_decimal(raw.get("Seguros")),
            commission_accum=self._to_decimal(raw.get("Comision")),
            platform_fee_accum=self._to_decimal(raw.get("Plataforma")),
            vat_accum=self._to_decimal(raw.get("IVA")),
            subproduct=self._normalize_str(raw.get("SUBPRODUCTO")),
            uvr_last_quote=self._to_decimal_or_none(raw.get("Cotizacion de UVR")),
            condonations_accum=self._to_decimal(raw.get("Condonaciones y/o descuentos")),
        )

    def _build_payment(self, raw: dict[str, Any]) -> PaymentRowData | None:
        payment_date = self._parse_date(raw.get("Fecha del pago"))
        if not payment_date:
            return None
        limit_date = self._parse_date(raw.get("Fecha limite de pago")) or payment_date
        return PaymentRowData(
            payment_date=payment_date,
            limit_pay_date=limit_date,
            payment_amount=self._to_decimal(raw.get("total")),
            installment_number=self._to_int_or_none(raw.get("Numero de la cuota que se cancela")),
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

    def _build_uvr_quote(self, raw: dict[str, Any]) -> UVRQuoteRowData | None:
        value = self._to_decimal_or_none(raw.get("Cotizacion de UVR"))
        if value is None:
            return None
        quote_date = self._parse_date(raw.get("Fecha de corte"))
        if not quote_date:
            return None
        return UVRQuoteRowData(quote_value=value, quote_date=quote_date)

    def _build_credit_adjustment(self, raw: dict[str, Any]) -> CreditAdjustmentRowData | None:
        amount = self._to_decimal_or_none(raw.get("Condonaciones y/o descuentos"))
        if amount is None:
            return None
        applied_date = self._parse_date(raw.get("Fecha de corte")) or datetime.now()
        return CreditAdjustmentRowData(
            adjustment_amount=amount,
            applied_date=applied_date,
        )

    # ------------------------------------------------------------------
    # Mappers
    # ------------------------------------------------------------------

    def _map_document_type(self, value: Any) -> UserDocumentType:
        raw = self._normalize_str(value)
        if raw:
            return _DOCUMENT_TYPE_MAP.get(raw.upper(), UserDocumentType.CC)
        return UserDocumentType.CC

    def _map_credit_type(self, value: Any) -> CreditTypes:
        raw = self._normalize_str(value)
        if raw:
            return _CREDIT_TYPE_MAP.get(raw.upper(), CreditTypes.FINANCIAL_ENTITY)
        return CreditTypes.FINANCIAL_ENTITY

    # ------------------------------------------------------------------
    # Normalizers
    # ------------------------------------------------------------------

    def _normalize_str(self, value: Any) -> str | None:
        if value is None:
            return None
        s = str(value).strip()
        if s.lower() in _NULL_STRINGS:
            return None
        return s

    def _normalize_phone(self, value: Any) -> str | None:
        # Kept as string intentionally to avoid int coercion issues with asyncpg
        return self._normalize_str(value)

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

    def _to_int(self, value: Any, default: int = 0) -> int:
        result = self._to_int_or_none(value)
        return result if result is not None else default

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
        for fmt in _DATE_FORMATS:
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        return None
