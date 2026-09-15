from enum import Enum


class TenantBillingLockStatus(str, Enum):
    NONE = "NINGUNO"
    WARNING = "ADVERTENCIA"
    PAYMENT_REQUIRED = "PAGO_REQUERIDO"
    BLOCKED = "BLOQUEADO"
