"""Estados posibles de un enlace de pago de Bold."""

from enum import StrEnum


class BoldLinkStatus(StrEnum):
    ACTIVE = "ACTIVE"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
