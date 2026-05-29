import uuid
from dataclasses import dataclass
from datetime import datetime

from pydantic import field_serializer, field_validator

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
    label: str
    case_type: SupportCaseType
    description: str
    icon: str

    @field_serializer("case_type")
    def serialize_case_type(self, v: SupportCaseType) -> str:
        return _CASE_TYPE_OUT.get(v, v.value)


_CASE_TYPE_IN = {
    "incident": SupportCaseType.INCIDENT,
    "requirement": SupportCaseType.REQUIREMENT,
    **{ct.value: ct for ct in SupportCaseType},
}


class CreateTicketSchema(BaseSchema):
    organization_id: uuid.UUID
    title: str
    case_type: SupportCaseType
    notes: str

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
    id: uuid.UUID
    name: str


class ResolveTicketSchema(BaseSchema):
    approved: bool
    notes: str


class UpdateTicketStatusSchema(BaseSchema):
    status: SupportTicketStatus

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
    user_id: int


class SupportTicketSchema(BaseSchema):
    id: uuid.UUID
    ticket_number: int
    case_type: SupportCaseType
    status: SupportTicketStatus
    organization_id: uuid.UUID
    organization_name: str = ""
    created_by: int
    assigned_to: int | None
    title: str | None
    notes: str | None
    resolved_at: datetime | None
    created_at: datetime

    @field_serializer("case_type")
    def serialize_case_type(self, v: SupportCaseType) -> str:
        return _CASE_TYPE_OUT.get(v, v.value)

    @field_serializer("status")
    def serialize_status(self, v: SupportTicketStatus) -> str:
        return _STATUS_OUT.get(v, v.value)


class TicketAttachmentSchema(BaseSchema):
    name: str
    url: str
    size: int


class OrgDocSchema(BaseSchema):
    label: str
    url: str | None


class OrgDocsSchema(BaseSchema):
    org_name: str
    documents: list[OrgDocSchema]
