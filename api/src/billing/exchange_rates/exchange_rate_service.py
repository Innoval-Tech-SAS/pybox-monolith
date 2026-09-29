"""Tasa de cambio USD -> moneda local, con fallback si la fuente externa falla."""

from decimal import Decimal, InvalidOperation

import httpx

from billing.exchange_rates.constants.exchange_rate_constants import (
    EXCHANGE_RATE_FALLBACK_BY_CURRENCY,
    EXCHANGE_RATE_TIMEOUT_MS,
    MARKET_RATE_API_URL,
    MARKET_RATE_CURRENCIES,
    TRM_API_URL,
)
from core.config.logger import logger


class ExchangeRateService:
    async def get_usd_rate(self, currency: str) -> Decimal:
        """
        Retorna la tasa de cambio USD -> `currency`. COP usa la TRM oficial; el resto
        de monedas soportadas usa una API de mercado generica. Si la consulta falla,
        la moneda no tiene fuente configurada, o el valor no es valido, cae al
        fallback fijo de esa moneda.
        """
        fallback = Decimal(EXCHANGE_RATE_FALLBACK_BY_CURRENCY.get(currency, "1"))

        if currency == "COP":
            return await self._get_trm_rate(fallback)
        if currency in MARKET_RATE_CURRENCIES:
            return await self._get_market_rate(currency, fallback)

        logger.warning(
            "[exchange_rate] sin fuente configurada para %s, usando fallback %s",
            currency,
            fallback,
        )
        return fallback

    async def _get_trm_rate(self, fallback: Decimal) -> Decimal:
        timeout_ms = int(EXCHANGE_RATE_TIMEOUT_MS)
        try:
            async with httpx.AsyncClient(timeout=timeout_ms / 1000) as client:
                response = await client.get(TRM_API_URL)
                response.raise_for_status()
                data = response.json()

            raw_value = data.get("valor")
            if raw_value is not None:
                value = Decimal(str(raw_value))
                if value > 0:
                    logger.info("[exchange_rate] COP obtenida desde TRM: %s", value)
                    return value

            logger.warning(
                "[exchange_rate] respuesta de TRM con formato inesperado, "
                "usando fallback %s",
                fallback,
            )
            return fallback
        except (httpx.HTTPError, InvalidOperation, ValueError, TypeError) as exc:
            logger.warning(
                "[exchange_rate] fallo la llamada a la TRM (%s), usando fallback %s",
                exc,
                fallback,
            )
            return fallback

    async def _get_market_rate(self, currency: str, fallback: Decimal) -> Decimal:
        timeout_ms = int(EXCHANGE_RATE_TIMEOUT_MS)
        try:
            async with httpx.AsyncClient(timeout=timeout_ms / 1000) as client:
                response = await client.get(MARKET_RATE_API_URL)
                response.raise_for_status()
                data = response.json()

            raw_value = (data.get("rates") or {}).get(currency)
            if raw_value is not None:
                value = Decimal(str(raw_value))
                if value > 0:
                    logger.info(
                        "[exchange_rate] %s obtenida desde API de mercado: %s",
                        currency,
                        value,
                    )
                    return value

            logger.warning(
                "[exchange_rate] %s no encontrada en respuesta de mercado, "
                "usando fallback %s",
                currency,
                fallback,
            )
            return fallback
        except (httpx.HTTPError, InvalidOperation, ValueError, TypeError) as exc:
            logger.warning(
                "[exchange_rate] fallo la llamada a la API de mercado para "
                "%s (%s), usando fallback %s",
                currency,
                exc,
                fallback,
            )
            return fallback
