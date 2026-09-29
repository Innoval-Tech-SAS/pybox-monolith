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
