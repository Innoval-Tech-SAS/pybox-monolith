from enum import Enum


class SupportCaseType(str, Enum):
    INCIDENT = "Incidente"
    REQUIREMENT = "Requerimiento"


class SupportTicketStatus(str, Enum):
    OPEN = "Abierto"
    IN_PROGRESS = "En Proceso"
    RESOLVED = "Resuelto"
