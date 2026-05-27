from enum import Enum


class SupportCaseType(str, Enum):
    INCIDENT = "incident"
    REQUIREMENT = "requirement"


class SupportTicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
