# COP usa la TRM oficial (Superintendencia Financiera de Colombia) via dolarapi.com;
# es la misma fuente que ya estaba en produccion antes de soportar otras monedas.
# Docs: https://dolarapi.com/docs/colombia/operations/get-trm
TRM_API_URL = "https://co.dolarapi.com/v1/trm"

# MX, AR, PE (y VE, aunque hoy no tiene pasarela de pago) no tienen una API oficial
# unificada por pais, asi que se usa una sola API de mercado que cubre todas las
# monedas en una consulta. Docs: https://www.exchangerate-api.com/docs/free
MARKET_RATE_API_URL = "https://open.er-api.com/v6/latest/USD"
MARKET_RATE_CURRENCIES = {"MXN", "ARS", "PEN", "VES"}

EXCHANGE_RATE_FALLBACK_BY_CURRENCY: dict[str, str] = {
    "COP": "4200",
    "MXN": "18",
    "ARS": "1460",
    "PEN": "3.8",
    "VES": "600",
}

EXCHANGE_RATE_TIMEOUT_MS = "5000"
