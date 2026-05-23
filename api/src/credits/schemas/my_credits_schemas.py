from datetime import datetime

from pydantic import BaseModel

from credits.enums.credit_enums import CreditTypes
from debtors.enums.debtor_enums import DebtorType


class MyCreditResponse(BaseModel):
    id: int
    credit_number: str
    credit_type: CreditTypes
    credit_date: datetime | None
    disbursed_date: datetime
    court_date: datetime | None
    total_credit_balance: float
    overdue_principal_balance: float
    current_interest: float
    overdue_interest: float
    days_overdue_at_cutoff: int
    overdue_installments: int
    pending_installments: int
    role: DebtorType

    class Config:
        from_attributes = True
