"""Parámetros de facturación mensual (impuestos, plazos, bloqueo) por entorno."""

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from dotenv import load_dotenv

from core.tools.config_tools import get_or_default

load_dotenv()

# Reutilizar un intento solo si el enlace sigue activo y tiene menos de 1 hora
# de antiguedad. Bold elimina referencias de prueba a las 12 h; se usa 1 h
# para ser conservadores.
ATTEMPT_TTL = timedelta(hours=1)

# Defaults de los parámetros de facturación configurables por entorno (BillingConfig,
# abajo) -- nombrados para no repetir el literal en cada `get_or_default`, no para
# desactivar la lectura de la variable de entorno: siguen siendo overrideables.
DEFAULT_TAX_ENABLED = "false"
DEFAULT_TAX_TYPE = "IVA"
DEFAULT_TAX_RATE = "0.19"
DEFAULT_PAYMENT_DUE_DAYS = "10"
DEFAULT_BLOCK_AFTER_DAYS = "20"
DEFAULT_BLOCKING_ENABLED = "true"


@dataclass
class BillingConfig:
    """Parámetros de facturación mensual. Todos son opcionales: si la variable
    no está definida se usa el default, que es el valor con el que ya venía
    corriendo el sistema.

    blocking_enabled es la válvula de escape del corte de envíos: con "false"
    ninguna organización queda bloqueada por factura vencida, sin importar el
    canal. Afecta tanto al corte (BillingStatusService.is_blocked) como a la
    transición a BLOCKED del cron.
    """

    tax_enabled: bool = (
        get_or_default("BILLING_TAX_ENABLED", DEFAULT_TAX_ENABLED) == "true"
    )
    tax_type: str = get_or_default("BILLING_TAX_TYPE", DEFAULT_TAX_TYPE)
    tax_rate: Decimal = Decimal(get_or_default("BILLING_TAX_RATE", DEFAULT_TAX_RATE))
    payment_due_days: int = int(
        get_or_default("BILLING_PAYMENT_DUE_DAYS", DEFAULT_PAYMENT_DUE_DAYS)
    )
    block_after_days: int = int(
        get_or_default("BILLING_BLOCK_AFTER_DAYS", DEFAULT_BLOCK_AFTER_DAYS)
    )
    blocking_enabled: bool = (
        get_or_default("BILLING_BLOCKING_ENABLED", DEFAULT_BLOCKING_ENABLED) != "false"
    )


billing_config = BillingConfig()
