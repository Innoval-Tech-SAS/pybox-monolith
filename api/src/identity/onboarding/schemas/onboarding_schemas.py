from enum import Enum

from pydantic import Field, field_validator

from core.base.schema_base import BaseSchema
from core.security.utils.password_policy import validate_password_strength
from identity.auth.enums.notification_enums import VerificationChannel
from identity.organizations.enums.organization_enums import EntitySectors
from identity.users.enums.user_enums import IdentityVerificationStatus


class RequestOtpSchema(BaseSchema):
    channel: VerificationChannel = Field(
        description="Canal de envío del OTP: EMAIL o PHONE"
    )


class VerifyOtpSchema(BaseSchema):
    channel: VerificationChannel = Field(description="Canal usado para el OTP")
    code: str = Field(description="Código OTP recibido")


class UpdateProfileSchema(BaseSchema):
    # Códigos validados contra la DB en el servicio (paises_tipos_documento),
    # no enum estático.
    document_type: str = Field(description="Código del tipo de documento de identidad")
    document_number: str = Field(description="Número de documento")
    nationality: str = Field(description="Código de país de la nacionalidad")


class OnboardingRepMode(str, Enum):
    SELF = "self"
    CREATE = "create"


class OrganizationOnboardingSchema(BaseSchema):
    name: str = Field(description="Nombre de la organización")
    sector: EntitySectors = Field(description="Sector al que pertenece la entidad")
    country: str = Field(description="Código de país de la organización")
    fiscal_document_number: str = Field(description="Número de documento fiscal")
    representative_mode: OnboardingRepMode = Field(
        description="Modo del representante: self (el mismo usuario) "
        "o create (nuevo usuario)"
    )
    rep_firstname: str | None = Field(
        default=None, description="Nombre del representante (si mode=create)"
    )
    rep_lastname: str | None = Field(
        default=None, description="Apellido del representante"
    )
    rep_email: str | None = Field(default=None, description="Correo del representante")
    rep_document_type: str | None = Field(
        default=None, description="Código del tipo de documento del representante"
    )
    rep_document_number: str | None = Field(
        default=None, description="Número de documento del representante"
    )
    rep_password: str | None = Field(
        default=None, description="Contraseña del representante (si mode=create)"
    )

    @field_validator("rep_password")
    @classmethod
    def validate_rep_password(cls, password: str | None) -> str | None:
        if password is None:
            return password
        return validate_password_strength(password)


class SetOnboardingPasswordSchema(BaseSchema):
    new_password: str = Field(description="Nueva contraseña")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, password: str) -> str:
        return validate_password_strength(password)


class SetPhoneSchema(BaseSchema):
    phone_number: str = Field(
        description="Número de teléfono con prefijo internacional"
    )


class OnboardingStatusSchema(BaseSchema):
    email_verified: bool = Field(description="Correo verificado")
    phone_set: bool = Field(description="Teléfono registrado")
    phone_verified: bool = Field(description="Teléfono verificado")
    document_complete: bool = Field(description="Documento de identidad completado")
    org_complete: bool | None = Field(
        description="Organización creada (solo para administradores)"
    )
    identity_verification_status: IdentityVerificationStatus | None = Field(
        default=None,
        description="Estado de verificación de identidad (solo para titulares SELF)",
    )
    must_change_password: bool = Field(
        description="El usuario debe cambiar su contraseña"
    )
    is_complete: bool = Field(
        description="Indica si el onboarding está completamente terminado"
    )
    missing_steps: list[str] = Field(description="Lista de pasos pendientes")


class IdentityDocumentSubmittedSchema(BaseSchema):
    identity_verification_status: IdentityVerificationStatus = Field(
        description="Estado de verificación de identidad tras la subida (PENDIENTE)"
    )
