from enum import StrEnum


class ReceivablesGatewayProvider(StrEnum):
    """Pasarelas con las que una ORGANIZACIÓN cobra a sus propios deudores, usando la
    cuenta propia de esa organización (la plataforma nunca recibe ni dispersa esos
    fondos). Distinto de `billing.provider_credentials`, que es la pasarela con la que
    PYBOX cobra a la organización — ver skill `wompi-gateway` para el detalle de
    integración de cada una."""

    WOMPI = "WOMPI"
    BOLD = "BOLD"
    PAYU = "PAYU"
    EPAYCO = "EPAYCO"


class ReceivablesPaymentAttemptStatus(StrEnum):
    """Estado de un intento de cobro contra una cuota (`PaymentModel`). Mismo
    vocabulario que usa Wompi para el estado de una transacción (ver skill
    `wompi-gateway`, Paso 8) — no se traduce dos veces al mapear la
    respuesta/webhook."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    ERROR = "ERROR"
    VOIDED = "VOIDED"


class ChargeMode(StrEnum):
    """Cómo se originó un intento de cobro (ver skill `wompi-gateway`, Paso 6).

    CHECKOUT: el deudor está presente y confirma el pago (tarjeta con challenge 3DS,
    PSE, Nequi push, Botón Bancolombia). AUTOMATIC_3RI: cobro silencioso contra una
    fuente de pago guardada, sin que el deudor interactúe — solo posible si la fuente
    quedó habilitada para 3RI (Mastercard + challenge 3DS previo + activación de
    fraude de Wompi para la organización)."""

    CHECKOUT = "CHECKOUT"
    AUTOMATIC_3RI = "AUTOMATIC_3RI"


class PaymentSourceType(StrEnum):
    """Medio de pago tokenizado en una fuente de pago reutilizable de Wompi (ver
    skill `wompi-gateway`, Paso 5). Fuera de alcance por ahora: BANCOLOMBIA_TRANSFER
    y PSE no soportan fuente de pago reutilizable en la API de Wompi."""

    CARD = "CARD"
    NEQUI = "NEQUI"


class PaymentSourceStatus(StrEnum):
    """Estado de una fuente de pago en Wompi (`POST /payment_sources`). Solo
    AVAILABLE puede usarse para cobrar."""

    PENDING = "PENDING"
    AVAILABLE = "AVAILABLE"
    DECLINED = "DECLINED"
    ERROR = "ERROR"
