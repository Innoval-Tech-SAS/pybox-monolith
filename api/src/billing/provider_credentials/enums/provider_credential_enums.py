from enum import StrEnum


class PlatformGatewayProvider(StrEnum):
    """Pasarelas con las que PYBOX cobra la suscripción/consumo a sus organizaciones
    clientes (billing propio de la plataforma). Distinto de las pasarelas que una
    organización usa para cobrarle a SUS deudores — ver
    `receivables.payment_gateways`."""

    MERCADOPAGO = "MERCADOPAGO"
    BOLD = "BOLD"
