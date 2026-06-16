from datetime import datetime

from pydantic import Field

from core.base.schema_base import BaseSchema
from collections.credits.enums.credit_enums import CreditTypes
from collections.debtors.enums.debtor_enums import DebtorType


class PaymentSummary(BaseSchema):
    id: int = Field(description="ID del pago")
    limit_pay_date: datetime = Field(description="Fecha límite de pago")
    payment_date: datetime | None = Field(default=None, description="Fecha en que se realizó el pago")
    payment_amount: float = Field(description="Monto pagado")
    installment_number: int | None = Field(default=None, description="Número de cuota")
    principal_payment: float = Field(description="Abono a capital")
    total_interest_amount: float = Field(description="Total de intereses")
    other_charges: float = Field(description="Otros cargos")


class CreditWithPayments(BaseSchema):
    id: int = Field(description="ID del crédito")
    credit_number: str = Field(description="Número de crédito")
    credit_type: CreditTypes = Field(description="Tipo de crédito")
    disbursed_date: datetime = Field(description="Fecha de desembolso")
    total_credit_balance: float = Field(description="Saldo total del crédito")
    overdue_principal_balance: float = Field(description="Saldo en mora (capital)")
    days_overdue_at_cutoff: int = Field(description="Días de mora al corte")
    role: DebtorType = Field(description="Rol del deudor en este crédito (Titular o Co-deudor)")
    organization_name: str = Field(description="Nombre de la organización acreedora")
    currency_code: str = Field(description="Código de moneda (COP, MXN, etc.)")
    payments: list[PaymentSummary] = Field(description="Historial de pagos")
