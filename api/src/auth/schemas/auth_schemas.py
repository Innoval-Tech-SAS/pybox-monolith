from __future__ import annotations

from pydantic import BaseModel, EmailStr, field_validator, model_validator

from auth.enums.auth_enums import AuthProvider
from base.schema_base import BaseSchema
from countries.enums.country_enums import DOCUMENTS_BY_NATIONALITY, Nationality, UserDocumentType


class UserCreate(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    password: str
    phone_number: str
    nationality: Nationality
    document_type: UserDocumentType | str | None = None
    document_number: str | None = None

    @model_validator(mode="after")
    def validate_document_for_nationality(self) -> "UserCreate":
        if self.document_type is None:
            return self
        doc = self.document_type
        if isinstance(doc, str):
            try:
                doc = UserDocumentType[doc]
            except KeyError:
                try:
                    doc = UserDocumentType(doc)
                except ValueError:
                    return self
        allowed = DOCUMENTS_BY_NATIONALITY.get(self.nationality, [])
        if doc not in allowed:
            raise ValueError(
                f"El tipo de documento '{doc}' no es válido para la nacionalidad '{self.nationality.value}'."
            )
        return self


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ProviderAuth(BaseModel):
    provider: AuthProvider | str
    token: str


class ProviderLogin(BaseModel):
    provider: AuthProvider | str
    token: str
    phone_number: str | None = None
    nationality: Nationality | str | None = None
    document_type: UserDocumentType | str | None = None
    document_number: str | None = None
    firstname: str | None = None
    lastname: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str
    auth_provider: str

    @field_validator("auth_provider", mode="before")
    @classmethod
    def coerce_auth_provider(cls, v: object) -> str:
        if isinstance(v, AuthProvider):
            return v.value
        return str(v)
