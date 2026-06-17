from enum import Enum


class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    OVERDUE = "OVERDUE"
    BLOCKED = "BLOCKED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class PaymentAttemptStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
