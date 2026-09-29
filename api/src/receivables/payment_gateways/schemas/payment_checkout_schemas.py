import uuid
from typing import Annotated, Literal, Union

from pydantic import EmailStr, Field

from core.base.schema_base import BaseSchema


class CardTransactionRequest(BaseSchema):
    payment_method_type: Literal["CARD"] = "CARD"
    token: str = Field(
        description=(
            "Token de la tarjeta ya tokenizada en el frontend (widget o /tokens/cards)"
        )
    )
    installments: int = Field(default=1, ge=1)
    customer_email: EmailStr


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
