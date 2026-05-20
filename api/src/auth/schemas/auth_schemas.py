from __future__ import annotations

from typing import NotRequired, TYPE_CHECKING, TypedDict

from auth.enums.auth_enums import AuthProvider
from users.enums.user_enums import UserDocumentType

if TYPE_CHECKING:
    from users.models.user_model import UserModel


class UserCreate(TypedDict):
    firstname: str
    lastname: str
    email: str
    password: str
    phone_number: str
    document_type: UserDocumentType | str
    document_number: str


class UserLogin(TypedDict):
    email: str
    password: str


class ProviderLogin(TypedDict):
    provider: AuthProvider | str
    token: str
    phone_number: str
    document_type: UserDocumentType | str
    document_number: str
    firstname: NotRequired[str]
    lastname: NotRequired[str]


class AuthResult(TypedDict):
    user: UserModel
    access_token: str
    token_type: str
    auth_provider: AuthProvider
