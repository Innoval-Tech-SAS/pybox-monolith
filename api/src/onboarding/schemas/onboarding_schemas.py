from pydantic import field_validator

from base.schema_base import BaseSchema
from countries.enums.country_enums import (
    Nationality,
    OrgFiscalDocumentType,
    OrgMercantileDocumentType,
    UserDocumentType,
    DOCUMENTS_BY_NATIONALITY,
)
from notifications.enums.notification_enums import VerificationChannel


class RequestOtpSchema(BaseSchema):
    channel: VerificationChannel


class VerifyOtpSchema(BaseSchema):
    channel: VerificationChannel
    code: str


class UpdateProfileSchema(BaseSchema):
    document_type: UserDocumentType
    document_number: str
    nationality: Nationality

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


class OrganizationOnboardingSchema(BaseSchema):
    name: str
    country: Nationality
    fiscal_document_number: str
    mercantile_document_number: str


class OnboardingStatusSchema(BaseSchema):
    email_verified: bool
    phone_verified: bool
    document_complete: bool
    org_complete: bool | None
    is_complete: bool
    missing_steps: list[str]
