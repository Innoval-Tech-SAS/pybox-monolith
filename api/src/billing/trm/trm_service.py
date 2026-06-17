import os
from decimal import Decimal, InvalidOperation

import httpx

from core.config.logger import logger

# TRM oficial (Superintendencia Financiera de Colombia) vía dolarapi.com.
# Docs: https://dolarapi.com/docs/colombia/operations/get-trm
_DEFAULT_TRM_API_URL = "https://co.dolarapi.com/v1/trm"


async def get_current_trm() -> Decimal:
    """
    Retorna la tasa de cambio USD -> COP (TRM) oficial vigente, consultada desde
    _DEFAULT_TRM_API_URL. Si la consulta falla o el valor no es valido, cae al
    valor fijo de BILLING_TRM_FALLBACK.
    """
    fallback = Decimal(os.getenv("BILLING_TRM_FALLBACK") or "4200")
    timeout_ms = int(os.getenv("BILLING_TRM_TIMEOUT_MS") or "5000")

    try:
        async with httpx.AsyncClient(timeout=timeout_ms / 1000) as client:
            response = await client.get(_DEFAULT_TRM_API_URL)
            response.raise_for_status()
            data = response.json()

        raw_value = data.get("valor")
        if raw_value is not None:
            value = Decimal(str(raw_value))
            if value > 0:
                logger.info("[trm] obtenida desde API: %s", value)
                return value

        logger.warning("[trm] respuesta de API con formato inesperado, usando fallback %s", fallback)
        return fallback
    except (httpx.HTTPError, InvalidOperation, ValueError, TypeError) as exc:
        logger.warning("[trm] fallo la llamada a la API (%s), usando fallback %s", exc, fallback)
        return fallback
