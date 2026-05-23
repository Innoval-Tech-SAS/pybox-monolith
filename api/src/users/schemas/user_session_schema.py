from pydantic import BaseModel

from users.enums.user_enums import UserRole, UserScope


class OrgSessionEntry(BaseModel):
    role: UserRole
    scope: UserScope
    org_name: str


class UserSession(BaseModel):
    full_name: str
    email: str
    role: UserRole | None = None
    scope: UserScope | None = None
    orgs: dict[str, OrgSessionEntry] = {}
