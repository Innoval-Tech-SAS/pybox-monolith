from datetime import datetime

from base.schema_base import BaseSchema
from credits.enums.credit_enums import CreditTypes
from debtors.enums.debtor_enums import DebtorType


class PaymentSummary(BaseSchema):
    id: int
    limit_pay_date: datetime
    payment_date: datetime | None
    payment_amount: float
    installment_number: int | None
    principal_payment: float
    total_interest_amount: float
    other_charges: float


class CreditWithPayments(BaseSchema):
    id: int
    credit_number: str
    credit_type: CreditTypes
    disbursed_date: datetime
    total_credit_balance: float
    overdue_principal_balance: float
    days_overdue_at_cutoff: int
    role: DebtorType
    organization_name: str
    currency_code: str
    payments: list[PaymentSummary]
