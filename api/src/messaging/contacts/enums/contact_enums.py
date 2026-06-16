from enum import StrEnum

class ContactStatus(StrEnum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"

    # Eventos reportados por 360NRS (webhook / reports-by-sending), 1:1 con el campo `event`
    OPENED = "OPENED"
    CLICKED = "CLICKED"
    UNSUBSCRIBED = "UNSUBSCRIBED"
    HARD_BOUNCED = "HARD_BOUNCED"
    SOFT_BOUNCED = "SOFT_BOUNCED"
    UNDELIVERED = "UNDELIVERED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    COMPLAINT = "COMPLAINT"
    UNSUBSCRIBED_LANDING = "UNSUBSCRIBED_LANDING"
    FORM_OPENED = "FORM_OPENED"
    FORM_SUBMITTED = "FORM_SUBMITTED"
    FORM_REJECTED = "FORM_REJECTED"




class ProviderType(StrEnum):
    NRS360 = "360nrs"