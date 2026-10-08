"""ExchangeRateService probado como unidad: `httpx.AsyncClient` se reemplaza por un
MagicMock que actua como context manager async (sin pytest-mock, sin red real). Foco:
que un fallo de red, una respuesta con formato inesperado, o un valor no numerico
jamas propague una excepcion -- siempre debe caer al fallback fijo de la moneda, para
que la generacion mensual de facturas (billing_cron_service.py) nunca se caiga por una
API de terceros caida."""

import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock

from billing.exchange_rates.constants.exchange_rate_constants import EXCHANGE_RATE_FALLBACK_BY_CURRENCY
from billing.exchange_rates.exchange_rate_service import ExchangeRateService

MODULE = "billing.exchange_rates.exchange_rate_service"


def _fake_async_client(*, result=None, exception: Exception | None = None) -> MagicMock:
    """Simula `async with httpx.AsyncClient(...) as client: await client.get(...)`."""
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    if exception is not None:
        client.get = AsyncMock(side_effect=exception)
    else:
        client.get = AsyncMock(return_value=result)
    return client


def _response(json_body: dict) -> MagicMock:
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json = MagicMock(return_value=json_body)
    return response


def _patch_async_client(monkeypatch, client: MagicMock) -> None:
    monkeypatch.setattr(f"{MODULE}.httpx.AsyncClient", MagicMock(return_value=client))


class TestGetUsdRateDispatch:
    async def test_cop_uses_trm_source(self, monkeypatch):
        client = _fake_async_client(result=_response({"valor": "4300.50"}))
        _patch_async_client(monkeypatch, client)

        rate = await ExchangeRateService().get_usd_rate("COP")

        assert rate == pytest.approx(4300.50)
        client.get.assert_awaited_once()

    async def test_market_currency_uses_market_source(self, monkeypatch):
        client = _fake_async_client(result=_response({"rates": {"MXN": "18.75"}}))
        _patch_async_client(monkeypatch, client)

        rate = await ExchangeRateService().get_usd_rate("MXN")

        assert rate == pytest.approx(18.75)
        client.get.assert_awaited_once()

    async def test_currency_without_source_returns_fallback_without_http_call(self, monkeypatch):
        constructor = MagicMock()
        monkeypatch.setattr(f"{MODULE}.httpx.AsyncClient", constructor)

        rate = await ExchangeRateService().get_usd_rate("BRL")

        # "BRL" no esta en EXCHANGE_RATE_FALLBACK_BY_CURRENCY ni en MARKET_RATE_CURRENCIES:
        # cae al fallback generico "1" sin tocar la red.
        from decimal import Decimal

        assert rate == Decimal("1")
        constructor.assert_not_called()


class TestGetTrmRate:
    async def test_valid_value_is_returned(self, monkeypatch):
        client = _fake_async_client(result=_response({"valor": "4200.75"}))
        _patch_async_client(monkeypatch, client)

        from decimal import Decimal

        rate = await ExchangeRateService()._get_trm_rate(Decimal("4200"))

        assert rate == Decimal("4200.75")

    async def test_missing_valor_key_falls_back(self, monkeypatch):
        from decimal import Decimal

        client = _fake_async_client(result=_response({"otra_cosa": "x"}))
        _patch_async_client(monkeypatch, client)

        rate = await ExchangeRateService()._get_trm_rate(Decimal("4200"))

        assert rate == Decimal("4200")

    async def test_zero_valor_falls_back(self, monkeypatch):
        from decimal import Decimal

        client = _fake_async_client(result=_response({"valor": "0"}))
        _patch_async_client(monkeypatch, client)

        rate = await ExchangeRateService()._get_trm_rate(Decimal("4200"))

        assert rate == Decimal("4200")

    async def test_negative_valor_falls_back(self, monkeypatch):
        from decimal import Decimal

        client = _fake_async_client(result=_response({"valor": "-5"}))
        _patch_async_client(monkeypatch, client)

        rate = await ExchangeRateService()._get_trm_rate(Decimal("4200"))

        assert rate == Decimal("4200")

    async def test_non_numeric_valor_falls_back_instead_of_raising(self, monkeypatch):
        from decimal import Decimal

        client = _fake_async_client(result=_response({"valor": "no-es-un-numero"}))
        _patch_async_client(monkeypatch, client)

        rate = await ExchangeRateService()._get_trm_rate(Decimal("4200"))

        assert rate == Decimal("4200")

    async def test_http_error_falls_back(self, monkeypatch):
        from decimal import Decimal

        client = _fake_async_client(exception=httpx.ConnectError("timeout"))
        _patch_async_client(monkeypatch, client)

        rate = await ExchangeRateService()._get_trm_rate(Decimal("4200"))

        assert rate == Decimal("4200")

    async def test_http_status_error_on_raise_for_status_falls_back(self, monkeypatch):
        from decimal import Decimal

        response = MagicMock()
        request = httpx.Request("GET", "https://co.dolarapi.com/v1/trm")
        response.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "error", request=request, response=httpx.Response(500, request=request)
            )
        )
        client = _fake_async_client(result=response)
        _patch_async_client(monkeypatch, client)

        rate = await ExchangeRateService()._get_trm_rate(Decimal("4200"))

        assert rate == Decimal("4200")


class TestGetMarketRate:
    async def test_valid_rate_is_returned(self, monkeypatch):
        from decimal import Decimal

        client = _fake_async_client(result=_response({"rates": {"ARS": "1450.20"}}))
        _patch_async_client(monkeypatch, client)

        rate = await ExchangeRateService()._get_market_rate("ARS", Decimal("1460"))

        assert rate == Decimal("1450.20")

    async def test_missing_currency_in_rates_falls_back(self, monkeypatch):
        from decimal import Decimal

        client = _fake_async_client(result=_response({"rates": {"MXN": "18"}}))
        _patch_async_client(monkeypatch, client)

        rate = await ExchangeRateService()._get_market_rate("PEN", Decimal("3.8"))

        assert rate == Decimal("3.8")

    async def test_missing_rates_key_falls_back(self, monkeypatch):
        from decimal import Decimal

        client = _fake_async_client(result=_response({}))
        _patch_async_client(monkeypatch, client)

        rate = await ExchangeRateService()._get_market_rate("PEN", Decimal("3.8"))

        assert rate == Decimal("3.8")

    async def test_http_error_falls_back(self, monkeypatch):
        from decimal import Decimal

        client = _fake_async_client(exception=httpx.ReadTimeout("timeout"))
        _patch_async_client(monkeypatch, client)

        rate = await ExchangeRateService()._get_market_rate("VES", Decimal("600"))

        assert rate == Decimal("600")

    async def test_fallback_matches_configured_value_per_currency(self, monkeypatch):
        # Confirma que el fallback usado por get_usd_rate es el de la moneda pedida, no
        # un valor generico -- si se rompiera el .get(currency) de la constante, todas
        # las monedas caerian al mismo valor y esto lo detectaria.
        from decimal import Decimal

        client = _fake_async_client(exception=httpx.ReadTimeout("timeout"))
        _patch_async_client(monkeypatch, client)

        rate = await ExchangeRateService().get_usd_rate("PEN")

        assert rate == Decimal(EXCHANGE_RATE_FALLBACK_BY_CURRENCY["PEN"])
