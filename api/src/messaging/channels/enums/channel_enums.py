from enum import StrEnum


class ChannelName(StrEnum):
    SMS = "SMS"
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    CALL = "CALL"
    CALL_IA = "CALL_IA"


class Currency(StrEnum):
    USD = "USD"
    EUR = "EUR"
    COP = "COP"
    MXN = "MXN"
