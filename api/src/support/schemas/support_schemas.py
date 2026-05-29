import uuid
from dataclasses import dataclass
from datetime import datetime

from pydantic import Field, field_serializer, field_validator

from base.schema_base import BaseSchema
from support.enums.support_enums import SupportCaseType, SupportTicketStatus


@dataclass
class SupportFilter:
    org_ids: list[uuid.UUID] | None = None
    created_by: int | None = None
    include_resolved: bool = False
    can_resolve: bool = False
    can_assign: bool = False
    can_create: bool = False
    can_escalate: bool = False
    route_to_global: bool = False
    check_portfolio_access: bool = False


_CASE_TYPE_OUT = {
    SupportCaseType.INCIDENT: "incident",
    SupportCaseType.REQUIREMENT: "requirement",
}

_STATUS_OUT = {
    SupportTicketStatus.OPEN: "open",
    SupportTicketStatus.IN_PROGRESS: "in_progress",
    SupportTicketStatus.RESOLVED: "resolved",
}

_STATUS_IN = {
    "open": SupportTicketStatus.OPEN,
    "in_progress": SupportTicketStatus.IN_PROGRESS,
    "resolved": SupportTicketStatus.RESOLVED,
    **{s.value: s for s in SupportTicketStatus},
}


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
    organization_id: uuid.UUID = Field(description="ID de la organización a la que pertenece el ticket")
    title: str = Field(description="Título del ticket")
    case_type: SupportCaseType = Field(description="Tipo de caso: incident o requirement")
    notes: str = Field(description="Descripción detallada del caso")

    @field_validator("case_type", mode="before")
    @classmethod
    def coerce_case_type(cls, v: object) -> SupportCaseType:
        if isinstance(v, SupportCaseType):
            return v
        mapped = _CASE_TYPE_IN.get(str(v))
        if mapped is None:
            raise ValueError(f"Tipo de caso inválido: {v!r}")
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


class AssignTicketSchema(BaseSchema):
    user_id: int = Field(description="ID del agente al que se asigna el ticket")


class SupportTicketSchema(BaseSchema):
    id: uuid.UUID = Field(description="ID único del ticket")
    ticket_number: int = Field(description="Número secuencial del ticket")
    case_type: SupportCaseType = Field(description="Tipo de caso")
    status: SupportTicketStatus = Field(description="Estado actual del ticket")
    organization_id: uuid.UUID = Field(description="ID de la organización")
    organization_name: str = Field(default="", description="Nombre de la organización")
    created_by: int = Field(description="ID del usuario que creó el ticket")
    assigned_to: int | None = Field(description="ID del agente asignado")
    title: str | None = Field(description="Título del ticket")
    notes: str | None = Field(description="Notas o descripción")
    resolved_at: datetime | None = Field(description="Fecha de resolución")
    created_at: datetime = Field(description="Fecha de creación")

    @field_serializer("case_type")
    def serialize_case_type(self, v: SupportCaseType) -> str:
        return _CASE_TYPE_OUT.get(v, v.value)

    @field_serializer("status")
    def serialize_status(self, v: SupportTicketStatus) -> str:
        return _STATUS_OUT.get(v, v.value)


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
