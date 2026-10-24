"""Schemas de verificación de identidad del deudor (challenge/verify)."""

from typing import Annotated

from pydantic import Field, StringConstraints

from app_platform.countries.enums.country_enums import UserDocumentType
from core.base.schema_base import BaseSchema
from receivables.debtors.enums.debtor_identity_enums import IdentityChannel

DocumentNumber = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=40)
]
ConfirmationValue = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=254)
]


class IdentityChallengeRequest(BaseSchema):
    document_type: UserDocumentType = Field(
        description="Tipo de documento de identidad"
    )
    document_number: DocumentNumber = Field(
        description="Número de documento, tal como se cargó"
    )


class IdentityChallengeResponse(BaseSchema):
    available: bool = Field(
        description=(
            "False si no hay a quién validar: documento inexistente o sin "
            "ningún dato de contacto"
        )
    )
    channel: IdentityChannel | None = Field(
        default=None, description="Dato que el titular debe confirmar"
    )
    hint: str | None = Field(
        default=None, description="Pista enmascarada del dato a confirmar"
    )


class IdentityVerifyRequest(BaseSchema):
    document_type: UserDocumentType = Field(
        description="Tipo de documento de identidad"
    )
    document_number: DocumentNumber = Field(
        description="Número de documento, tal como se cargó"
    )
    channel: IdentityChannel = Field(description="Dato con el que se confirma")
    value: ConfirmationValue = Field(description="Valor que escribió el titular")


class IdentityVerifyResponse(BaseSchema):
    verified: bool = Field(
        description="True si el valor coincide con un dato registrado del titular"
    )
