"""Parámetros internos de entrada para crear una factura (no expuestos en la API)."""

import uuid
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class InvoiceItemInput:
    campaign_id: uuid.UUID | None
    campaign_name: str
    channel_id: uuid.UUID
    channel_name: str
    base_currency: str
    quantity: int
    subtotal_base: Decimal


@dataclass
class CreateInvoiceParams:
    organization_id: uuid.UUID
    period_year: int
    period_month: int
    exchange_rate: Decimal
    billing_currency: str = "COP"
    items: list[InvoiceItemInput] = field(default_factory=list)
