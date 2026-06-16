from enum import Enum

from messaging.constants import channels


class TemplateChannel(str, Enum):
    EMAIL = channels.EMAIL
    SMS = channels.SMS
    WHATSAPP = channels.WHATSAPP
    CALL = channels.CALL


class TemplateStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
