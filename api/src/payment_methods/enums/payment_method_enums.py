from enum import Enum


class PaymentMethodType(str, Enum):
    BANK_TRANSFER = "BANK_TRANSFER"
    CASH_DEPOSIT = "CASH_DEPOSIT"
    QR = "QR"
    PAYMENT_LINK = "PAYMENT_LINK"
    CASH = "CASH"
    OTHER = "OTHER"
