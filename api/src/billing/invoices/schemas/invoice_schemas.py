"""Schemas de respuesta de facturas: items, admin y checkout de pago."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import Field

from billing.invoices.enums.invoice_enums import InvoiceStatus, PaymentAttemptStatus
from core.base.schema_base import BaseSchema


class InvoiceItemResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID del item de factura")
    invoice_id: uuid.UUID = Field(description="ID de la factura")
    campaign_id: uuid.UUID | None = Field(
        default=None, description="ID de la campaña facturada"
    )
    campaign_name: str = Field(
        description="Nombre de la campaña al momento de facturar"
    )
    channel_id: uuid.UUID = Field(description="ID del canal")
    channel_name: str = Field(description="Nombre del canal al momento de facturar")
    base_currency: str = Field(description="Moneda base del precio unitario")
    unit_price_base: Decimal = Field(
        description="Precio unitario promedio en moneda base"
    )
    quantity: int = Field(description="Cantidad de mensajes facturados")
    subtotal_base: Decimal = Field(description="Subtotal en moneda base")


class PaymentAttemptResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID del intento de pago")
    invoice_id: uuid.UUID = Field(description="ID de la factura")
    attempt_number: int = Field(description="Numero de intento")
    provider: str = Field(
        description="Pasarela de pago del intento (ej. 'BOLD', 'MERCADO_PAGO')"
    )
    provider_reference: str | None = Field(
        default=None, description="Referencia enviada al proveedor"
    )
    provider_link_id: str | None = Field(
        default=None, description="ID del enlace de pago del proveedor"
    )
    payment_url: str | None = Field(default=None, description="URL del enlace de pago")
    status: PaymentAttemptStatus = Field(description="Estado del intento de pago")
    created_at: datetime = Field(description="Fecha de creacion del intento")


class InvoiceResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID de la factura")
    organization_id: uuid.UUID = Field(description="ID de la organizacion")
    period_year: int = Field(description="Anio del periodo facturado")
    period_month: int = Field(description="Mes del periodo facturado")
    base_currency: str = Field(description="Moneda base")
    billing_currency: str = Field(description="Moneda de facturacion")
    exchange_rate: Decimal = Field(description="Tasa de cambio usada")
    subtotal_base_amount: Decimal = Field(description="Subtotal en moneda base")
    subtotal_billing_amount: Decimal = Field(
        description="Subtotal en moneda de facturacion"
    )
    tax_type: str = Field(description="Tipo de impuesto aplicado")
    tax_rate: Decimal = Field(description="Tasa de impuesto aplicada")
    tax_amount: Decimal = Field(description="Monto de impuesto")
    total_amount: Decimal = Field(description="Monto total a pagar")
    status: InvoiceStatus = Field(description="Estado de la factura")
    issued_at: datetime | None = Field(default=None, description="Fecha de emision")
    due_at: datetime | None = Field(default=None, description="Fecha de vencimiento")
    block_at: datetime | None = Field(default=None, description="Fecha de bloqueo")
    paid_at: datetime | None = Field(default=None, description="Fecha de pago")
    created_at: datetime = Field(description="Fecha de creacion")
    updated_at: datetime | None = Field(
        default=None, description="Fecha de actualizacion"
    )
    items: list[InvoiceItemResponse] = Field(
        default_factory=list, description="Items facturados"
    )
    attempts: list[PaymentAttemptResponse] = Field(
        default_factory=list, description="Intentos de pago"
    )


class CurrentInvoiceResponse(BaseSchema):
    invoice: InvoiceResponse | None = Field(
        default=None, description="Factura vigente de la organizacion"
    )


class ListInvoicesResponse(BaseSchema):
    invoices: list[InvoiceResponse] = Field(description="Facturas de la organizacion")
    total: int = Field(description="Total de facturas")
    page: int = Field(description="Pagina actual")
    limit: int = Field(description="Tamano de pagina")
    total_pages: int = Field(description="Total de paginas")


class AdminInvoiceResponse(InvoiceResponse):
    organization_name: str = Field(
        description="Nombre de la organizacion duenia de la factura"
    )


class AdminListInvoicesResponse(BaseSchema):
    invoices: list[AdminInvoiceResponse] = Field(
        description="Facturas de todas las organizaciones"
    )
    total: int = Field(description="Total de facturas")
    page: int = Field(description="Pagina actual")
    limit: int = Field(description="Tamano de pagina")
    total_pages: int = Field(description="Total de paginas")


class MercadoPagoChargeRequest(BaseSchema):
    token: str = Field(
        description="Token de tarjeta generado en el frontend via Secure Fields"
    )
    payment_method_id: str = Field(
        description=(
            "ID del medio de pago (ej. 'master', 'visa', 'debmaster'), de "
            "mp.getPaymentMethods"
        )
    )
    payment_type_id: str = Field(
        default="credit_card",
        description=(
            "Tipo del medio ('credit_card' o 'debit_card'), de "
            "mp.getPaymentMethods; debe corresponder al payment_method_id"
        ),
    )
    installments: int = Field(default=1, ge=1, description="Numero de cuotas")


class PaymentLinkResponse(BaseSchema):
    provider: str = Field(
        description="Pasarela de pago usada (ej. 'BOLD', 'MERCADO_PAGO')"
    )
    order_id: str = Field(description="Referencia del intento ante el proveedor")
    amount: int = Field(
        description="Monto del cobro en unidades enteras de la moneda de facturacion"
    )
    currency: str = Field(description="Moneda del cobro")
    description: str = Field(description="Descripcion del cobro")
    tax_type: str = Field(description="Tipo de impuesto de la factura")
    attempt_id: uuid.UUID = Field(description="ID del intento de pago")
    reused: bool = Field(description="Indica si se reutilizo un intento existente")
    provider_payload: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Datos especificos del proveedor que el frontend necesita para "
            "renderizar el boton/widget de pago"
        ),
    )
