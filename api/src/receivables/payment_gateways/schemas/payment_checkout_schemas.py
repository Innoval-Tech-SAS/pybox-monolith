"""Schemas de checkout: métodos de pago y transacciones contra la pasarela."""

import uuid
from typing import Annotated, Literal, Union

from pydantic import EmailStr, Field

from core.base.schema_base import BaseSchema


class BrowserInfoRequest(BaseSchema):
    """Fingerprint del navegador del deudor, exigido por Wompi para 3D Secure v2 en
    pagos con tarjeta (ver skill `wompi-gateway`, Paso 6)."""

    browser_color_depth: str
    browser_screen_height: str
    browser_screen_width: str
    browser_language: str
    browser_user_agent: str
    browser_tz: str


class CardTransactionRequest(BaseSchema):
    payment_method_type: Literal["CARD"] = "CARD"
    number: str
    cvc: str
    exp_month: str
    exp_year: str
    card_holder: str
    installments: int = Field(default=1, ge=1)
    customer_email: EmailStr
    browser_info: BrowserInfoRequest


class PseTransactionRequest(BaseSchema):
    payment_method_type: Literal["PSE"] = "PSE"
    user_type: int = Field(description="0 = persona natural, 1 = persona jurídica")
    user_legal_id_type: str
    user_legal_id: str
    financial_institution_code: str
    payment_description: str
    customer_email: EmailStr


class NequiTransactionRequest(BaseSchema):
    payment_method_type: Literal["NEQUI"] = "NEQUI"
    phone_number: str
    customer_email: EmailStr


class BancolombiaTransferTransactionRequest(BaseSchema):
    payment_method_type: Literal["BANCOLOMBIA_TRANSFER"] = "BANCOLOMBIA_TRANSFER"
    payment_description: str
    customer_email: EmailStr


TransactionRequest = Annotated[
    Union[
        CardTransactionRequest,
        PseTransactionRequest,
        NequiTransactionRequest,
        BancolombiaTransferTransactionRequest,
    ],
    Field(discriminator="payment_method_type"),
]


class PaymentAttemptResponse(BaseSchema):
    id: uuid.UUID
    status: str
    provider_reference: str | None
    provider_transaction_id: str | None
    charge_mode: str


class ThreeDsChallengeResponse(BaseSchema):
    current_step: str
    current_step_status: str
    challenge_html: str


class TransactionCreationResponse(BaseSchema):
    attempt: PaymentAttemptResponse
    three_ds_challenge: ThreeDsChallengeResponse | None = None


class TokenizeCardSourceRequest(BaseSchema):
    number: str
    cvc: str
    exp_month: str
    exp_year: str
    card_holder: str
    customer_email: EmailStr


class TokenizeNequiSourceRequest(BaseSchema):
    phone_number: str
    customer_email: EmailStr


class PaymentSourceResponse(BaseSchema):
    id: uuid.UUID
    type: str
    status: str
    masked_identifier: str | None
    brand: str | None
    is_active: bool


class FinancialInstitutionResponse(BaseSchema):
    financial_institution_code: str
    financial_institution_name: str
