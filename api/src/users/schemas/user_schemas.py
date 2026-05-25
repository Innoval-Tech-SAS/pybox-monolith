from __future__ import annotations

from datetime import datetime

from auth.enums.auth_enums import AuthProvider
from base.schema_base import BaseSchema
from countries.enums.country_enums import Nationality, UserDocumentType


class UserSummarySchema(BaseSchema):
    id: int
    full_name: str
    email: str


class RoleEntrySchema(BaseSchema):
    role: str
    scope: str
    org_id: str | None = None
    org_name: str | None = None


class AdminUserSummarySchema(BaseSchema):
    id: int
    full_name: str
    email: str
    is_active: bool
    created_at: datetime | None
    roles: list[RoleEntrySchema] = []


class AdminUserDetailSchema(AdminUserSummarySchema):
    firstname: str
    lastname: str
    phone_number: str | None
    auth_provider: str
    document_type: str | None
    document_number: str | None
    is_email_verified: bool
    is_phone_verified: bool
    mfa_enabled: bool
    is_active_sessions: bool
    updated_at: datetime | None


class UpdateUserSchema(BaseSchema):
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    phone_number: str | None = None
    is_active: bool | None = None


class UserProfile(BaseSchema):
    id: int
    firstname: str
    lastname: str
    email: str
    phone_number: str | None
    auth_provider: AuthProvider
    nationality: Nationality | None
    document_type: UserDocumentType | None
    document_number: str | None
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None
