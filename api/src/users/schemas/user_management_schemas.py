from pydantic import EmailStr

from base.schema_base import BaseSchema
from users.enums.user_enums import PermissionEffect, UserRole


class ManagedUserCreate(BaseSchema):
    firstname: str
    lastname: str
    email: EmailStr
    phone_number: str
    password: str
    role: UserRole


class ManagedUserResponse(BaseSchema):
    id: int
    full_name: str
    email: str
    phone_number: str
    role: str
    scope: str


class PermissionAssignRequest(BaseSchema):
    name: str
    effect: PermissionEffect


class PermissionEntry(BaseSchema):
    name: str
    effect: str


class PermissionListResponse(BaseSchema):
    permissions: list[PermissionEntry]
