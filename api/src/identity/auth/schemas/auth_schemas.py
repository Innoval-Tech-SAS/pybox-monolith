from __future__ import annotations

from pydantic import EmailStr, Field, field_validator

from identity.auth.enums.auth_enums import AuthProvider
from core.base.schema_base import BaseSchema
from core.security.utils.password_policy import validate_password_strength
from identity.auth.enums.notification_enums import VerificationChannel


class UserCreate(BaseSchema):
    firstname: str = Field(description="Nombre del usuario")
    lastname: str = Field(description="Apellido del usuario")
    email: EmailStr = Field(description="Correo electrónico")
    password: str = Field(description="Contraseña")
    phone_number: str = Field(description="Número de teléfono con prefijo internacional")
    # nationality/document_type son códigos validados contra la DB en el servicio
    # (paises / paises_tipos_documento), no contra un enum estático.
    nationality: str = Field(description="Código de país de la nacionalidad del usuario")
    document_type: str | None = Field(default=None, description="Código del tipo de documento de identidad")
    document_number: str | None = Field(default=None, description="Número de documento de identidad")

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        return validate_password_strength(password)


class UserLogin(BaseSchema):
    email: EmailStr = Field(description="Correo electrónico")
    password: str = Field(description="Contraseña")


class ProviderAuth(BaseSchema):
    provider: AuthProvider | str = Field(description="Proveedor OAuth (google, facebook, etc.)")
    token: str = Field(description="Token de acceso del proveedor")


class ProviderLogin(BaseSchema):
    provider: AuthProvider | str = Field(description="Proveedor OAuth")
    token: str = Field(description="Token de acceso del proveedor")
    phone_number: str | None = Field(default=None, description="Número de teléfono")
    nationality: str | None = Field(default=None, description="Código de país de la nacionalidad")
    document_type: str | None = Field(default=None, description="Código del tipo de documento")
    document_number: str | None = Field(default=None, description="Número de documento")
    firstname: str | None = Field(default=None, description="Nombre")
    lastname: str | None = Field(default=None, description="Apellido")


class ChangePasswordSchema(BaseSchema):
    current_password: str = Field(description="Contraseña actual")
    new_password: str = Field(description="Nueva contraseña")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, password: str) -> str:
        return validate_password_strength(password)


class ForgotPasswordLookupSchema(BaseSchema):
    document_type: str = Field(description="Código del tipo de documento de identidad")
    document_number: str = Field(description="Número de documento de identidad")


class ForgotPasswordLookupResponse(BaseSchema):
    masked_email: str | None = Field(description="Email enmascarado (ej: j***@g***.com)")
    masked_phone: str | None = Field(description="Teléfono enmascarado (ej: +57 3** ***67)")


class ForgotPasswordSendCodeSchema(BaseSchema):
    document_type: str = Field(description="Código del tipo de documento de identidad")
    document_number: str = Field(description="Número de documento de identidad")
    channel: VerificationChannel = Field(description="Canal de envío del código (EMAIL o SMS)")


class ForgotPasswordVerifyCodeSchema(BaseSchema):
    document_type: str = Field(description="Código del tipo de documento de identidad")
    document_number: str = Field(description="Número de documento de identidad")
    code: str = Field(description="Código de verificación recibido")
    channel: VerificationChannel = Field(description="Canal por el que se recibió el código")


class ResetPasswordSchema(BaseSchema):
    document_type: str = Field(description="Código del tipo de documento de identidad")
    document_number: str = Field(description="Número de documento de identidad")
    code: str = Field(description="Código de verificación recibido")
    channel: VerificationChannel = Field(description="Canal por el que se recibió el código")
    new_password: str = Field(description="Nueva contraseña")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, password: str) -> str:
        return validate_password_strength(password)


class RefreshRequest(BaseSchema):
    # Opcional: si el cliente usa cookies httpOnly, el refresh token viaja en la
    # cookie y no necesita enviarse en el body.
    refresh_token: str | None = Field(default=None, description="Token de actualización")


class AuthResponse(BaseSchema):
    # access_token/refresh_token viajan solo como cookie httpOnly (ver set_auth_cookies);
    # exclude=True los mantiene disponibles para el controller (que sí los necesita para
    # setear las cookies) sin duplicarlos en el body de la respuesta JSON.
    access_token: str = Field(description="Token de acceso JWT", exclude=True)
    refresh_token: str = Field(description="Token de actualización", exclude=True)
    token_type: str = Field(description="Tipo de token (Bearer)")
    auth_provider: str = Field(description="Proveedor de autenticación utilizado")

    @field_validator("auth_provider", mode="before")
    @classmethod
    def coerce_auth_provider(cls, v: object) -> str:
        if isinstance(v, AuthProvider):
            return v.value
        return str(v)
