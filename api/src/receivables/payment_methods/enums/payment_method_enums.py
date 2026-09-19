from enum import Enum


class PaymentMethodType(str, Enum):
    BANK_TRANSFER = "TRANSFERENCIA_BANCARIA"
    CASH_DEPOSIT = "CONSIGNACION_EFECTIVO"
    QR = "QR"  # código, no se traduce
    PAYMENT_LINK = "ENLACE_PAGO"
    CASH = "EFECTIVO"
    OTHER = "OTRO"
