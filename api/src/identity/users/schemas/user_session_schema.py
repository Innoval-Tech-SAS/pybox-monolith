from datetime import datetime
import uuid

from pydantic import Field

from core.base.schema_base import BaseSchema
from identity.organizations.enums.organization_enums import VerificationStatus
from identity.users.enums.user_enums import UserRole, UserScope

SESSION_KEY_PREFIX = "session:"


def session_key(user_id: uuid.UUID | str | int) -> str:
    return f"{SESSION_KEY_PREFIX}{user_id}"


class OrgSessionEntry(BaseSchema):
    role: UserRole = Field(description="Rol del usuario dentro de esta organización")
    org_name: str = Field(description="Nombre de la organización")
    permissions: frozenset[str] = Field(default_factory=frozenset, description="Permisos efectivos del usuario en esta organización")
    verification_status: VerificationStatus = Field(default=VerificationStatus.PENDING, description="Estado de verificación de la organización")
    created_at: datetime | None = Field(default=None, description="Fecha en que el usuario obtuvo acceso a la organización")


class UserSession(BaseSchema):
    user_id: uuid.UUID = Field(description="ID del usuario autenticado")
    full_name: str = Field(description="Nombre completo del usuario")
    email: str = Field(description="Correo electrónico del usuario")
    role: UserRole | None = Field(default=None, description="Rol activo en el contexto actual")
    scope: UserScope | None = Field(default=None, description="Ámbito de la sesión: GLOBAL, ORGANIZATION o SELF")
    document_type: str | None = Field(default=None, description="Tipo de documento de identidad (usuarios SELF)")
    document_number: str | None = Field(default=None, description="Número de documento de identidad")
    profile_photo_url: str | None = Field(default=None, description="URL de la foto de perfil")
    must_change_password: bool = Field(default=False, description="Indica si el usuario debe cambiar su contraseña antes de continuar")
    mfa_enabled: bool = Field(default=True, description="Indica si la autenticación multifactor está habilitada")
    orgs: dict[str, OrgSessionEntry] = Field(default_factory=dict, description="Organizaciones a las que pertenece el usuario, indexadas por ID")

    @property
    def is_global(self) -> bool:
        return self.scope == UserScope.GLOBAL

    @property
    def is_self(self) -> bool:
        return self.scope == UserScope.SELF
