from enum import Enum


class DebtorType(str, Enum):
    DEBTOR = "Titular"
    CO_DEBTOR = "Co-deudor"
