from enum import Enum


class ContactStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
