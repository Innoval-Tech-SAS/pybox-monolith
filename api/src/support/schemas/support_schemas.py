import uuid
from dataclasses import dataclass
from datetime import datetime

from pydantic import Field, field_serializer, field_validator

from base.schema_base import BaseSchema
from support.enums.support_enums import SupportCaseType, SupportTicketEventType, SupportTicketPriority, SupportTicketStatus


@dataclass
class SupportFilter:
    # Access control
    org_ids: list[uuid.UUID] | None = None
    created_by: int | None = None
    include_resolved: bool = False
    can_resolve: bool = False
    can_assign: bool = False
    can_create: bool = False
    can_escalate: bool = False
    route_to_global: bool = False
    check_portfolio_access: bool = False
    # Search / filters
    q: str | None = None
    status_filter: SupportTicketStatus | None = None
    priority_filter: SupportTicketPriority | None = None
    case_type_filter: SupportCaseType | None = None
    assigned_to_filter: int | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None


_CASE_TYPE_OUT = {
    SupportCaseType.INCIDENT: "incident",
    SupportCaseType.REQUIREMENT: "requirement",
}

_STATUS_OUT = {
    SupportTicketStatus.NEW: "new",
    SupportTicketStatus.OPEN: "open",
    SupportTicketStatus.IN_PROGRESS: "in_progress",
    SupportTicketStatus.PENDING_CLIENT: "pending_client",
    SupportTicketStatus.PENDING_THIRD: "pending_third",
    SupportTicketStatus.RESOLVED: "resolved",
    SupportTicketStatus.CLOSED: "closed",
}

_STATUS_IN = {
    **{k: v for k, v in _STATUS_OUT.items()},  # English keys → enum (inverted below)
    **{s.value: s for s in SupportTicketStatus},
}
# Invert _STATUS_OUT to build the "key → enum" mapping
_STATUS_IN = {v: k for k, v in _STATUS_OUT.items()} | {s.value: s for s in SupportTicketStatus}

_PRIORITY_OUT = {
    SupportTicketPriority.LOW: "low",
    SupportTicketPriority.MEDIUM: "medium",
    SupportTicketPriority.HIGH: "high",
    SupportTicketPriority.URGENT: "urgent",
}

_PRIORITY_IN = {v: k for k, v in _PRIORITY_OUT.items()} | {p.value: p for p in SupportTicketPriority}


class TicketCategorySchema(BaseSchema):
    label: str = Field(description="Nombre de la categoría")
    case_type: SupportCaseType = Field(description="Tipo de caso: incident o requirement")
    description: str = Field(description="Descripción de la categoría")
    icon: str = Field(description="Nombre del icono")

    @field_serializer("case_type")
    def serialize_case_type(self, v: SupportCaseType) -> str:
        return _CASE_TYPE_OUT.get(v, v.value)


_CASE_TYPE_IN = {
    "incident": SupportCaseType.INCIDENT,
    "requirement": SupportCaseType.REQUIREMENT,
    **{ct.value: ct for ct in SupportCaseType},
}


class CreateTicketSchema(BaseSchema):
    organization_id: uuid.UUID | None = Field(default=None, description="ID de la organización (obligatorio para scope ORG y SELF)")
    title: str = Field(description="Título del ticket")
    case_type: SupportCaseType = Field(description="Tipo de caso: incident o requirement")
    notes: str = Field(description="Descripción detallada del caso")
    priority: SupportTicketPriority = Field(default=SupportTicketPriority.MEDIUM, description="Prioridad del ticket")

    @field_validator("case_type", mode="before")
    @classmethod
    def coerce_case_type(cls, v: object) -> SupportCaseType:
        if isinstance(v, SupportCaseType):
            return v
        mapped = _CASE_TYPE_IN.get(str(v))
        if mapped is None:
            raise ValueError(f"Tipo de caso inválido: {v!r}")
        return mapped

    @field_validator("priority", mode="before")
    @classmethod
    def coerce_priority(cls, v: object) -> SupportTicketPriority:
        if isinstance(v, SupportTicketPriority):
            return v
        mapped = _PRIORITY_IN.get(str(v))
        if mapped is None:
            raise ValueError(f"Prioridad inválida: {v!r}")
        return mapped


class TicketOrgSchema(BaseSchema):
    id: uuid.UUID = Field(description="ID de la organización")
    name: str = Field(description="Nombre de la organización")


class ResolveTicketSchema(BaseSchema):
    approved: bool = Field(description="True si la resolución fue aprobada por el cliente")
    notes: str = Field(description="Notas de cierre")


class UpdateTicketStatusSchema(BaseSchema):
    status: SupportTicketStatus = Field(description="Nuevo estado del ticket")

    @field_validator("status", mode="before")
    @classmethod
    def coerce_status(cls, v: object) -> SupportTicketStatus:
        if isinstance(v, SupportTicketStatus):
            return v
        mapped = _STATUS_IN.get(str(v))
        if mapped is None:
            raise ValueError(f"Estado inválido: {v!r}")
        return mapped


class UpdateTicketPrioritySchema(BaseSchema):
    priority: SupportTicketPriority = Field(description="Nueva prioridad del ticket")

    @field_validator("priority", mode="before")
    @classmethod
    def coerce_priority(cls, v: object) -> SupportTicketPriority:
        if isinstance(v, SupportTicketPriority):
            return v
        mapped = _PRIORITY_IN.get(str(v))
        if mapped is None:
            raise ValueError(f"Prioridad inválida: {v!r}")
        return mapped


class AssignTicketSchema(BaseSchema):
    user_id: int = Field(description="ID del agente al que se asigna el ticket")


class SupportTicketSchema(BaseSchema):
    id: uuid.UUID = Field(description="ID único del ticket")
    ticket_number: int = Field(description="Número secuencial del ticket")
    case_type: SupportCaseType = Field(description="Tipo de caso")
    status: SupportTicketStatus = Field(description="Estado actual del ticket")
    priority: SupportTicketPriority = Field(description="Prioridad del ticket")
    organization_id: uuid.UUID | None = Field(description="ID de la organización")
    organization_name: str = Field(default="", description="Nombre de la organización")
    created_by: int = Field(description="ID del usuario que creó el ticket")
    assigned_to: int | None = Field(description="ID del agente asignado")
    title: str | None = Field(description="Título del ticket")
    notes: str | None = Field(description="Notas o descripción")
    resolved_at: datetime | None = Field(description="Fecha de resolución")
    closed_at: datetime | None = Field(default=None, description="Fecha de cierre")
    created_at: datetime = Field(description="Fecha de creación")

    @field_serializer("case_type")
    def serialize_case_type(self, v: SupportCaseType) -> str:
        return _CASE_TYPE_OUT.get(v, v.value)

    @field_serializer("status")
    def serialize_status(self, v: SupportTicketStatus) -> str:
        return _STATUS_OUT.get(v, v.value)

    @field_serializer("priority")
    def serialize_priority(self, v: SupportTicketPriority) -> str:
        return _PRIORITY_OUT.get(v, v.value)


class TicketAttachmentSchema(BaseSchema):
    name: str = Field(description="Nombre del archivo")
    url: str = Field(description="URL de descarga")
    size: int = Field(description="Tamaño en bytes")


class OrgDocSchema(BaseSchema):
    label: str = Field(description="Etiqueta del documento")
    url: str | None = Field(description="URL del documento")


class OrgDocsSchema(BaseSchema):
    org_name: str = Field(description="Nombre de la organización")
    documents: list[OrgDocSchema] = Field(description="Lista de documentos de verificación")


class CreateMessageSchema(BaseSchema):
    body: str = Field(description="Contenido del mensaje", min_length=1, max_length=4000)
    is_internal: bool = Field(default=False, description="True si el mensaje es solo para agentes")


class TicketMessageSchema(BaseSchema):
    id: uuid.UUID = Field(description="ID del mensaje")
    ticket_id: uuid.UUID = Field(description="ID del ticket")
    sender_id: int = Field(description="ID del remitente")
    body: str = Field(description="Contenido del mensaje")
    is_internal: bool = Field(description="Mensaje interno de agente")
    created_at: datetime = Field(description="Fecha de envío")


class TicketEventSchema(BaseSchema):
    id: uuid.UUID = Field(description="ID del evento")
    ticket_id: uuid.UUID = Field(description="ID del ticket")
    user_id: int = Field(description="ID del usuario que realizó la acción")
    event_type: SupportTicketEventType = Field(description="Tipo de evento")
    from_value: str | None = Field(description="Valor anterior")
    to_value: str | None = Field(description="Valor nuevo")
    created_at: datetime = Field(description="Fecha del evento")


class TicketMetricsSchema(BaseSchema):
    total: int = Field(description="Total de tickets")
    open: int = Field(description="Tickets abiertos o nuevos")
    in_progress: int = Field(description="Tickets en proceso")
    pending: int = Field(description="Tickets pendientes (cliente o tercero)")
    resolved: int = Field(description="Tickets resueltos")
    closed: int = Field(description="Tickets cerrados")
    created_today: int = Field(description="Tickets creados hoy")
    resolved_today: int = Field(description="Tickets resueltos hoy")
    avg_resolution_hours: float | None = Field(description="Tiempo promedio de resolución en horas")
    by_priority: dict[str, int] = Field(description="Tickets por prioridad")
