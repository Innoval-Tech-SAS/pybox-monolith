from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from auth.enums.auth_enums import AuthProvider
from base.schema_base import BaseSchema
from countries.enums.country_enums import DOCUMENTS_BY_NATIONALITY, Nationality, UserDocumentType


class UserCreate(BaseModel):
    firstname: str = Field(description="Nombre del usuario")
    lastname: str = Field(description="Apellido del usuario")
    email: EmailStr = Field(description="Correo electrónico")
    password: str = Field(description="Contraseña")
    phone_number: str = Field(description="Número de teléfono con prefijo internacional")
    nationality: Nationality = Field(description="Nacionalidad del usuario")
    document_type: UserDocumentType | str | None = Field(default=None, description="Tipo de documento de identidad")
    document_number: str | None = Field(default=None, description="Número de documento de identidad")

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
    email: EmailStr = Field(description="Correo electrónico")
    password: str = Field(description="Contraseña")


class ProviderAuth(BaseModel):
    provider: AuthProvider | str = Field(description="Proveedor OAuth (google, facebook, etc.)")
    token: str = Field(description="Token de acceso del proveedor")


class ProviderLogin(BaseModel):
    provider: AuthProvider | str = Field(description="Proveedor OAuth")
    token: str = Field(description="Token de acceso del proveedor")
    phone_number: str | None = Field(default=None, description="Número de teléfono")
    nationality: Nationality | str | None = Field(default=None, description="Nacionalidad")
    document_type: UserDocumentType | str | None = Field(default=None, description="Tipo de documento")
    document_number: str | None = Field(default=None, description="Número de documento")
    firstname: str | None = Field(default=None, description="Nombre")
    lastname: str | None = Field(default=None, description="Apellido")


class RefreshRequest(BaseModel):
    refresh_token: str = Field(description="Token de actualización")


class AuthResponse(BaseSchema):
    access_token: str = Field(description="Token de acceso JWT")
    refresh_token: str = Field(description="Token de actualización")
    token_type: str = Field(description="Tipo de token (Bearer)")
    auth_provider: str = Field(description="Proveedor de autenticación utilizado")

    @field_validator("auth_provider", mode="before")
    @classmethod
    def coerce_auth_provider(cls, v: object) -> str:
        if isinstance(v, AuthProvider):
            return v.value
        return str(v)
