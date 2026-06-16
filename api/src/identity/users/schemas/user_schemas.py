from __future__ import annotations

from datetime import datetime

from pydantic import Field, field_validator

from identity.auth.enums.auth_enums import AuthProvider
from core.base.schema_base import BaseSchema
from app_platform.countries.enums.country_enums import Nationality, UserDocumentType
from core.security.services.encrypt_service import encrypt_service


class UserSummarySchema(BaseSchema):
    id: int = Field(description="ID del usuario")
    full_name: str = Field(description="Nombre completo")
    email: str = Field(description="Correo electrónico")


class ChatAvailableUserSchema(BaseSchema):
    id: int = Field(description="ID del usuario")
    full_name: str = Field(description="Nombre completo")
    profile_photo_url: str | None = Field(default=None, description="URL de la foto de perfil")
    is_online: bool = Field(default=False, description="Indica si el usuario está en línea")


class RoleEntrySchema(BaseSchema):
    role: str = Field(description="Rol del usuario")
    scope: str = Field(description="Ámbito (GLOBAL u ORGANIZATION)")
    org_id: str | None = Field(default=None, description="ID de la organización")
    org_name: str | None = Field(default=None, description="Nombre de la organización")


class AdminUserSummarySchema(BaseSchema):
    id: int = Field(description="ID del usuario")
    full_name: str = Field(description="Nombre completo")
    email: str = Field(description="Correo electrónico")
    phone_number: str | None = Field(description="Número de teléfono")
    is_active: bool = Field(description="Indica si la cuenta está activa")
    created_at: datetime | None = Field(description="Fecha de creación")
    roles: list[RoleEntrySchema] = Field(default=[], description="Roles del usuario")


class AdminUserDetailSchema(AdminUserSummarySchema):
    firstname: str = Field(description="Nombre")
    lastname: str = Field(description="Apellido")
    phone_number: str | None = Field(description="Teléfono")
    auth_provider: str = Field(description="Proveedor de autenticación")
    document_type: str | None = Field(description="Tipo de documento")
    document_number: str | None = Field(description="Número de documento")
    is_email_verified: bool = Field(description="Correo verificado")
    is_phone_verified: bool = Field(description="Teléfono verificado")
    mfa_enabled: bool = Field(description="MFA habilitado")
    is_active_sessions: bool = Field(description="Tiene sesiones activas")
    updated_at: datetime | None = Field(description="Última actualización")
    profile_photo_url: str | None = Field(default=None, description="URL de foto de perfil")


class UpdateUserSchema(BaseSchema):
    firstname: str | None = Field(default=None, description="Nombre")
    lastname: str | None = Field(default=None, description="Apellido")
    email: str | None = Field(default=None, description="Correo electrónico")
    phone_number: str | None = Field(default=None, description="Teléfono")
    is_active: bool | None = Field(default=None, description="Activar o desactivar cuenta")
    document_type: UserDocumentType | None = Field(default=None, description="Tipo de documento")
    document_number: str | None = Field(default=None, description="Número de documento")
    mfa_enabled: bool | None = Field(default=None, description="Habilitar o deshabilitar MFA")


class ProfilePhotoSchema(BaseSchema):
    profile_photo_url: str = Field(description="URL pública de la foto de perfil actualizada")


class UserProfile(BaseSchema):
    id: int = Field(description="ID del usuario")
    firstname: str = Field(description="Nombre")
    lastname: str = Field(description="Apellido")
    email: str = Field(description="Correo electrónico")
    phone_number: str | None = Field(description="Teléfono")
    auth_provider: AuthProvider = Field(description="Proveedor de autenticación")
    nationality: Nationality | None = Field(description="Nacionalidad")
    document_type: UserDocumentType | None = Field(description="Tipo de documento")
    document_number: str | None = Field(description="Número de documento")
    is_active: bool = Field(description="Cuenta activa")
    created_at: datetime | None = Field(description="Fecha de creación")
    updated_at: datetime | None = Field(description="Última actualización")

    @field_validator("document_number", mode="before")
    @classmethod
    def decrypt_document(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return encrypt_service.decrypt_to_str(v)
