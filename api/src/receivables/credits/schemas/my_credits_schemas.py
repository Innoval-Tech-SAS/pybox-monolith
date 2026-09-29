import uuid
from datetime import datetime

from pydantic import Field

from core.base.schema_base import BaseSchema
from receivables.credits.enums.credit_enums import CreditTypes
from receivables.debtors.enums.debtor_enums import DebtorType


class PaymentMethodSummary(BaseSchema):
    id: uuid.UUID = Field(description="ID del método de pago")
    name: str = Field(description="Nombre del método de pago")
    type: str = Field(description="Tipo de método de pago")
    description: str | None = Field(default=None, description="Descripción")
    instructions: str | None = Field(default=None, description="Instrucciones de pago")
    bank_name: str | None = Field(default=None, description="Nombre del banco")
    account_type: str | None = Field(default=None, description="Tipo de cuenta")
    account_number: str | None = Field(default=None, description="Número de cuenta")
    payment_link: str | None = Field(default=None, description="Enlace de pago")
    qr_image_url: str | None = Field(default=None, description="URL de imagen QR")


class PaymentSummary(BaseSchema):
    id: uuid.UUID = Field(description="ID del pago")
    limit_pay_date: datetime = Field(description="Fecha límite de pago")
    payment_date: datetime | None = Field(
        default=None, description="Fecha en que se realizó el pago"
    )
    payment_amount: float = Field(description="Monto pagado")
    installment_number: int | None = Field(default=None, description="Número de cuota")
    principal_payment: float = Field(description="Abono a capital")
    total_interest_amount: float = Field(description="Total de intereses")
    other_charges: float = Field(description="Otros cargos")
    status: str = Field(
        description=(
            "Estado del pago (enum PaymentStatus: pendiente, "
            "reprogramacion_solicitada, reprogramado, validacion_solicitada, "
            "pagado)"
        )
    )


class CreditWithPayments(BaseSchema):
    id: uuid.UUID = Field(description="ID del crédito")
    credit_number: str = Field(description="Número de crédito")
    credit_type: CreditTypes = Field(description="Tipo de crédito")
    disbursed_date: datetime = Field(description="Fecha de desembolso")
    total_credit_balance: float = Field(description="Saldo total del crédito")
    overdue_principal_balance: float = Field(description="Saldo en mora (capital)")
    days_overdue_at_cutoff: int = Field(description="Días de mora al corte")
    role: DebtorType = Field(
        description="Rol del deudor en este crédito (Titular o Co-deudor)"
    )
    organization_name: str = Field(description="Nombre de la organización acreedora")
    currency_code: str = Field(description="Código de moneda (COP, MXN, etc.)")
    payments: list[PaymentSummary] = Field(description="Historial de pagos")
    payment_methods: list[PaymentMethodSummary] = Field(
        default_factory=list,
        description="Métodos de pago aceptados por la organización",
    )
    is_active: bool = Field(
        default=True, description="Si el crédito está vigente (False = dado de baja)"
    )
    settlement_requested: bool = Field(
        default=False,
        description="Si hay una solicitud de baja en curso (ticket abierto)",
    )
