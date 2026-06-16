from enum import Enum


class ChannelName(str, Enum):
    SMS = "SMS"
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    CALL = "CALL"


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    COP = "COP"
    MXN = "MXN"
