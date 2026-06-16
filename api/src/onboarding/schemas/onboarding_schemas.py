from enum import Enum

from pydantic import Field, field_validator

from base.schema_base import BaseSchema
from countries.enums.country_enums import (
    Nationality,
    OrgFiscalDocumentType,
    OrgMercantileDocumentType,
    UserDocumentType,
    DOCUMENTS_BY_NATIONALITY,
)
from auth.enums.notification_enums import VerificationChannel


class RequestOtpSchema(BaseSchema):
    channel: VerificationChannel = Field(description="Canal de envío del OTP: EMAIL o PHONE")


class VerifyOtpSchema(BaseSchema):
    channel: VerificationChannel = Field(description="Canal usado para el OTP")
    code: str = Field(description="Código OTP recibido")


class UpdateProfileSchema(BaseSchema):
    document_type: UserDocumentType = Field(description="Tipo de documento de identidad")
    document_number: str = Field(description="Número de documento")
    nationality: Nationality = Field(description="Nacionalidad")

    @field_validator("document_type")
    @classmethod
    def validate_document_for_nationality(
        cls, document_type: UserDocumentType, info
    ) -> UserDocumentType:
        nationality = info.data.get("nationality")
        if nationality and document_type not in DOCUMENTS_BY_NATIONALITY.get(nationality, []):
            raise ValueError(
                f"El tipo de documento {document_type} no es válido para {nationality}"
            )
        return document_type


class OnboardingRepMode(str, Enum):
    SELF = "self"
    CREATE = "create"


class OrganizationOnboardingSchema(BaseSchema):
    name: str = Field(description="Nombre de la organización")
    country: Nationality = Field(description="País de la organización")
    fiscal_document_number: str = Field(description="Número de documento fiscal")
    representative_mode: OnboardingRepMode = Field(description="Modo del representante: self (el mismo usuario) o create (nuevo usuario)")
    rep_firstname: str | None = Field(default=None, description="Nombre del representante (si mode=create)")
    rep_lastname: str | None = Field(default=None, description="Apellido del representante")
    rep_email: str | None = Field(default=None, description="Correo del representante")
    rep_document_type: UserDocumentType | None = Field(default=None, description="Tipo de documento del representante")
    rep_document_number: str | None = Field(default=None, description="Número de documento del representante")
    rep_password: str | None = Field(default=None, description="Contraseña del representante (si mode=create)")


class SetOnboardingPasswordSchema(BaseSchema):
    new_password: str = Field(description="Nueva contraseña")


class SetPhoneSchema(BaseSchema):
    phone_number: str = Field(description="Número de teléfono con prefijo internacional")


class OnboardingStatusSchema(BaseSchema):
    email_verified: bool = Field(description="Correo verificado")
    phone_set: bool = Field(description="Teléfono registrado")
    phone_verified: bool = Field(description="Teléfono verificado")
    document_complete: bool = Field(description="Documento de identidad completado")
    org_complete: bool | None = Field(description="Organización creada (solo para administradores)")
    must_change_password: bool = Field(description="El usuario debe cambiar su contraseña")
    is_complete: bool = Field(description="Indica si el onboarding está completamente terminado")
    missing_steps: list[str] = Field(description="Lista de pasos pendientes")
