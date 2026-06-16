from datetime import datetime
import uuid

from core.base.schema_base import BaseSchema
from identity.organizations.enums.organization_enums import VerificationStatus
from identity.users.enums.user_enums import UserRole, UserScope

SESSION_KEY_PREFIX = "session:"


def session_key(user_id: uuid.UUID | str | int) -> str:
    return f"{SESSION_KEY_PREFIX}{user_id}"


class OrgSessionEntry(BaseSchema):
    role: UserRole
    org_name: str
    permissions: frozenset[str] = frozenset()
    verification_status: VerificationStatus = VerificationStatus.PENDING
    created_at: datetime | None = None


class UserSession(BaseSchema):
    user_id: uuid.UUID
    full_name: str
    email: str
    role: UserRole | None = None
    scope: UserScope | None = None
    document_type: str | None = None   # identidad para usuarios SELF
    document_number: str | None = None
    profile_photo_url: str | None = None
    must_change_password: bool = False
    mfa_enabled: bool = True
    orgs: dict[str, OrgSessionEntry] = {}

    @property
    def is_global(self) -> bool:
        return self.scope == UserScope.GLOBAL

    @property
    def is_self(self) -> bool:
        return self.scope == UserScope.SELF
