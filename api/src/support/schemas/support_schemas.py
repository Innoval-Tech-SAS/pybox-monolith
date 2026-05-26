import uuid
from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel

from base.schema_base import BaseSchema
from support.enums.support_enums import SupportCaseType, SupportTicketStatus


@dataclass
class SupportFilter:
    org_ids: list[uuid.UUID] | None = None
    created_by: int | None = None
    include_resolved: bool = False
    can_resolve: bool = False
    can_assign: bool = False


class ResolveTicketSchema(BaseSchema):
    approved: bool
    notes: str | None = None


class AssignTicketSchema(BaseSchema):
    user_id: int


class SupportTicketSchema(BaseModel):
    id: int
    case_type: SupportCaseType
    status: SupportTicketStatus
    organization_id: uuid.UUID
    created_by: int
    assigned_to: int | None
    notes: str | None
    resolved_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
