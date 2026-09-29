import uuid
from datetime import datetime

from pydantic import Field

from core.base.schema_base import BaseSchema
from identity.organizations.enums.organization_enums import VerificationStatus
from identity.users.enums.user_enums import (
    IdentityVerificationStatus,
    UserRole,
    UserScope,
)

SESSION_KEY_PREFIX = "session:"
MFA_VERIFIED_KEY_PREFIX = "mfa_verified:"


def session_key(user_id: uuid.UUID | str | int) -> str:
    return f"{SESSION_KEY_PREFIX}{user_id}"


def mfa_verified_key(user_id: uuid.UUID | str | int) -> str:
    """Marca (con TTL) que el usuario ya superó el segundo factor en el login vigente.

    Vive separada de `UserSession` a propósito: `UserSession` se reconstruye por
    completo cada vez que cambian roles/permisos (`get_user_session`), y si el flag
    viviera ahí, cualquier refresco de sesión mid-login volvería a pedir MFA."""
    return f"{MFA_VERIFIED_KEY_PREFIX}{user_id}"


class OrgSessionEntry(BaseSchema):
    role: UserRole = Field(description="Rol del usuario dentro de esta organización")
    org_name: str = Field(description="Nombre de la organización")
    permissions: frozenset[str] = Field(
        default_factory=frozenset,
        description="Permisos efectivos del usuario en esta organización",
    )
    verification_status: VerificationStatus = Field(
        default=VerificationStatus.PENDING,
        description="Estado de verificación de la organización",
    )
    created_at: datetime | None = Field(
        default=None,
        description="Fecha en que el usuario obtuvo acceso a la organización",
    )


class UserSession(BaseSchema):
    user_id: uuid.UUID = Field(description="ID del usuario autenticado")
    full_name: str = Field(description="Nombre completo del usuario")
    email: str = Field(description="Correo electrónico del usuario")
    role: UserRole | None = Field(
        default=None, description="Rol activo en el contexto actual"
    )
    scope: UserScope | None = Field(
        default=None, description="Ámbito de la sesión: GLOBAL, ORGANIZATION o SELF"
    )
    document_type: str | None = Field(
        default=None, description="Tipo de documento de identidad (usuarios SELF)"
    )
    document_number_hash: str | None = Field(
        default=None,
        description=(
            "Hash del número de documento (para resolver al deudor propio). "
            "Nunca el valor en claro: la sesión se cachea en Redis y no debe "
            "guardar PII descifrada."
        ),
    )
    profile_photo_url: str | None = Field(
        default=None, description="URL de la foto de perfil"
    )
    identity_verification_status: IdentityVerificationStatus = Field(
        default=IdentityVerificationStatus.NOT_SUBMITTED,
        description=(
            "Estado de verificación de identidad (usuarios SELF) — gatea el "
            "acceso a créditos/extractos/notificaciones propias"
        ),
    )
    must_change_password: bool = Field(
        default=False,
        description=(
            "Indica si el usuario debe cambiar su contraseña antes de continuar"
        ),
    )
    mfa_enabled: bool = Field(
        default=True,
        description="Indica si la autenticación multifactor está habilitada",
    )
    orgs: dict[str, OrgSessionEntry] = Field(
        default_factory=dict,
        description="Organizaciones a las que pertenece el usuario, indexadas por ID",
    )

    @property
    def is_global(self) -> bool:
        return self.scope == UserScope.GLOBAL

    @property
    def is_self(self) -> bool:
        return self.scope == UserScope.SELF
