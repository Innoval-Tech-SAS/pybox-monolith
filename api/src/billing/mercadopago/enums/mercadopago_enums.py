from enum import StrEnum


class MercadoPagoOrderStatus(StrEnum):
    CREATED = "created"
    PROCESSED = "processed"
    PROCESSING = "processing"
    ACTION_REQUIRED = "action_required"
    CANCELED = "canceled"
    EXPIRED = "expired"
    FAILED = "failed"
    REFUNDED = "refunded"
    CHARGED_BACK = "charged_back"
