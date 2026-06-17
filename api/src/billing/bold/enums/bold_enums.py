from enum import Enum


class BoldLinkStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
