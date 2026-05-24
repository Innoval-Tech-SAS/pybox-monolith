from enum import Enum


class SupportCaseType(str, Enum):
    ORG_VERIFICATION = "org_verification"
    ERROR_REPORT = "error_report"


class SupportTicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
