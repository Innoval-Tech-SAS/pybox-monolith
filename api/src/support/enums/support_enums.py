from enum import Enum


class SupportCaseType(str, Enum):
    INCIDENT = "Incidente"
    REQUIREMENT = "Requerimiento"


class SupportTicketStatus(str, Enum):
    NEW = "Nuevo"
    OPEN = "Abierto"
    IN_PROGRESS = "En Proceso"
    PENDING_CLIENT = "Pendiente Cliente"
    PENDING_THIRD = "Pendiente Tercero"
    RESOLVED = "Resuelto"
    CLOSED = "Cerrado"


class SupportTicketPriority(str, Enum):
    LOW = "Baja"
    MEDIUM = "Media"
    HIGH = "Alta"
    URGENT = "Urgente"


class SupportTicketEventType(str, Enum):
    CREATED = "created"
    STATUS_CHANGED = "status_changed"
    PRIORITY_CHANGED = "priority_changed"
    ASSIGNED = "assigned"
    REASSIGNED = "reassigned"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"
