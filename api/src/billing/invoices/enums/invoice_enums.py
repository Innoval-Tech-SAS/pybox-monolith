"""Estados de factura, de intento de pago y proveedores de pasarela de facturación."""

from enum import Enum


class PaymentProvider(str, Enum):
    # Nombres de marca, no se traducen.
    BOLD = "BOLD"
    MERCADO_PAGO = "MERCADO_PAGO"


class InvoiceStatus(str, Enum):
    DRAFT = "BORRADOR"
    ISSUED = "EMITIDA"
    PAYMENT_PENDING = "PAGO_PENDIENTE"
    OVERDUE = "VENCIDA"
    BLOCKED = "BLOQUEADA"
    PAID = "PAGADA"
    CANCELLED = "CANCELADA"


class PaymentAttemptStatus(str, Enum):
    ACTIVE = "ACTIVO"
    PROCESSING = "PROCESANDO"
    PAID = "PAGADO"
    EXPIRED = "EXPIRADO"
    REJECTED = "RECHAZADO"
    CANCELLED = "CANCELADO"
