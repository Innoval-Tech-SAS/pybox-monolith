from enum import Enum


class TenantBillingLockStatus(str, Enum):
    NONE = "NONE"
    WARNING = "WARNING"
    PAYMENT_REQUIRED = "PAYMENT_REQUIRED"
    BLOCKED = "BLOCKED"
