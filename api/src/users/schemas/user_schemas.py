from __future__ import annotations

from datetime import datetime

from auth.enums.auth_enums import AuthProvider
from base.schema_base import BaseSchema
from countries.enums.country_enums import Nationality, UserDocumentType


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
