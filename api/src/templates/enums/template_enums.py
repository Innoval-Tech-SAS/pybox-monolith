from enum import Enum


class TemplateChannel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"


class TemplateStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
