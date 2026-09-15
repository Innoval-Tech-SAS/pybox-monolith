from decimal import Decimal

from pydantic import Field

from core.base.schema_base import BaseSchema
from billing.invoices.enums.invoice_enums import InvoiceStatus, PaymentProvider


class BillingSummaryResponse(BaseSchema):
    current_month_revenue: Decimal = Field(
        description="Suma (USD) de facturas emitidas en el periodo actual, excluyendo borradores y canceladas"
    )
    overdue_amount: Decimal = Field(
        description="Suma (USD) de facturas vencidas o bloqueadas, en todas las organizaciones"
    )
    billed_organizations_count: int = Field(
        description="Organizaciones con al menos una factura emitida en el periodo actual"
    )
    collection_rate: float = Field(
        description="Porcentaje del monto facturado (USD) en el periodo actual que ya esta en estado PAID"
    )


class InvoiceStatusBreakdownItem(BaseSchema):
    status: InvoiceStatus = Field(description="Estado de la factura")
    count: int = Field(description="Cantidad de facturas en este estado")
    total_amount: Decimal = Field(description="Suma (USD) de facturas en este estado")


class InvoiceStatusBreakdownResponse(BaseSchema):
    items: list[InvoiceStatusBreakdownItem] = Field(
        description="Desglose de facturas del periodo actual por estado"
    )


class RevenueByChannelItem(BaseSchema):
    channel_name: str = Field(description="Nombre del canal")
    total_amount: Decimal = Field(description="Suma (USD) facturada del canal en la ventana de 12 meses")


class RevenueByChannelResponse(BaseSchema):
    items: list[RevenueByChannelItem] = Field(description="Ingreso por canal en los ultimos 12 meses")


class RevenueByProviderItem(BaseSchema):
    provider: PaymentProvider = Field(description="Pasarela de pago")
    total_amount: Decimal = Field(description="Suma (USD) cobrada por la pasarela en la ventana de 12 meses")


class RevenueByProviderResponse(BaseSchema):
    items: list[RevenueByProviderItem] = Field(
        description="Ingreso de facturas pagadas atribuido a la pasarela que las cobro, ultimos 12 meses"
    )


class MonthlyRevenuePoint(BaseSchema):
    period: str = Field(description="Periodo en formato YYYY-MM")
    total_amount: Decimal = Field(description="Suma (USD) facturada en el periodo")


class MonthlyRevenueResponse(BaseSchema):
    points: list[MonthlyRevenuePoint] = Field(
        description="Facturacion mensual de los ultimos 12 meses, todas las organizaciones"
    )
