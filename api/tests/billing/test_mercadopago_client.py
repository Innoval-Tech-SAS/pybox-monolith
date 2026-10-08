"""MercadoPagoClient probado como unidad: `_http` (httpx.AsyncClient interno del
singleton) se reemplaza por un MagicMock con `.post`/`.get` como AsyncMock que
devuelven `httpx.Response` REALES (no mockeadas) -- asi `raise_for_status()`/`.json()`
se comportan exactamente como con la API real, sin pytest-mock ni red.

Foco: el area mas fragil del cliente (Orders API en modo manual) -- que
`add_transaction` omita `installments` en debito, que `process_order` distinga un
rechazo legitimo de MP (que SIGUE trayendo la orden en el body de error) de un fallo
real de la request, y que el email de sandbox solo se sustituya en development."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from billing.mercadopago.services.mercadopago_client import MercadoPagoClient

MODULE = "billing.mercadopago.services.mercadopago_client"


def make_client() -> MercadoPagoClient:
    """El cliente es un singleton (`__new__` reutiliza `_instance`): se resetea `_http`
    en cada test para no arrastrar mocks de un test a otro."""
    client = MercadoPagoClient()
    client._http = MagicMock()
    return client


def _response(status_code: int, *, json_body: dict | list | None = None, text: str | None = None) -> httpx.Response:
    request = httpx.Request("POST", "https://api.mercadopago.com/v1/orders")
    kwargs: dict = {}
    if text is not None:
        kwargs["text"] = text
    elif json_body is not None:
        kwargs["json"] = json_body
    return httpx.Response(status_code, request=request, **kwargs)


def _force_production_env(monkeypatch) -> None:
    monkeypatch.setattr(f"{MODULE}.get_or_throw", MagicMock(return_value="production"))


class TestCreateOrderManual:
    async def test_success_posts_expected_body_and_returns_json(self, monkeypatch):
        _force_production_env(monkeypatch)
        client = make_client()
        client._http.post = AsyncMock(
            return_value=_response(201, json_body={"id": "ORD1", "client_token": "tok-1"})
        )

        result = await client.create_order_manual("TOKEN", "INV-1", 15000, "Factura 2026-08", "user@example.com")

        assert result == {"id": "ORD1", "client_token": "tok-1"}
        _, kwargs = client._http.post.call_args
        body = kwargs["json"]
        assert body["processing_mode"] == "manual"
        assert body["external_reference"] == "INV-1"
        assert body["total_amount"] == "15000.00"
        assert body["payer"] == {"email": "user@example.com"}
        assert body["items"] == [{"title": "Factura 2026-08", "quantity": 1, "unit_price": "15000.00"}]
        assert kwargs["headers"]["Authorization"] == "Bearer TOKEN"
        assert kwargs["headers"]["X-Idempotency-Key"] == "INV-1"

    async def test_development_env_rewrites_payer_email_to_sandbox_domain(self, monkeypatch):
        monkeypatch.setattr(f"{MODULE}.get_or_throw", MagicMock(return_value="development"))
        client = make_client()
        client._http.post = AsyncMock(return_value=_response(201, json_body={"id": "ORD1"}))

        await client.create_order_manual("TOKEN", "INV-1", 15000, "desc", "real.user@gmail.com")

        _, kwargs = client._http.post.call_args
        assert kwargs["json"]["payer"]["email"] == "real.user@testuser.com"

    async def test_production_env_keeps_real_payer_email(self, monkeypatch):
        _force_production_env(monkeypatch)
        client = make_client()
        client._http.post = AsyncMock(return_value=_response(201, json_body={"id": "ORD1"}))

        await client.create_order_manual("TOKEN", "INV-1", 15000, "desc", "real.user@gmail.com")

        _, kwargs = client._http.post.call_args
        assert kwargs["json"]["payer"]["email"] == "real.user@gmail.com"

    async def test_error_response_raises_http_status_error(self, monkeypatch):
        _force_production_env(monkeypatch)
        client = make_client()
        client._http.post = AsyncMock(return_value=_response(400, json_body={"message": "invalid_email"}))

        with pytest.raises(httpx.HTTPStatusError):
            await client.create_order_manual("TOKEN", "INV-1", 15000, "desc", "user@example.com")


class TestGetOrder:
    async def test_success_returns_json(self):
        client = make_client()
        client._http.get = AsyncMock(return_value=_response(200, json_body={"id": "ORD1", "status": "created"}))

        result = await client.get_order("TOKEN", "ORD1")

        assert result == {"id": "ORD1", "status": "created"}
        _, kwargs = client._http.get.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer TOKEN"

    async def test_error_response_raises(self):
        client = make_client()
        client._http.get = AsyncMock(return_value=_response(404, json_body={"message": "not found"}))

        with pytest.raises(httpx.HTTPStatusError):
            await client.get_order("TOKEN", "ORD-DESCONOCIDA")


class TestAddTransaction:
    async def test_credit_card_includes_installments(self):
        client = make_client()
        client._http.post = AsyncMock(return_value=_response(200, json_body={"status": "created"}))

        await client.add_transaction("TOKEN", "ORD1", 150, "card-tok", "master", "credit_card", 3, "idem-1")

        _, kwargs = client._http.post.call_args
        payment_method = kwargs["json"]["payments"][0]["payment_method"]
        assert payment_method["installments"] == 3
        assert payment_method["id"] == "master"
        assert payment_method["type"] == "credit_card"
        assert kwargs["headers"]["X-Idempotency-Key"] == "idem-1"

    async def test_debit_card_omits_installments(self):
        client = make_client()
        client._http.post = AsyncMock(return_value=_response(200, json_body={"status": "created"}))

        await client.add_transaction("TOKEN", "ORD1", 150, "card-tok", "debmaster", "debit_card", 1, "idem-2")

        _, kwargs = client._http.post.call_args
        payment_method = kwargs["json"]["payments"][0]["payment_method"]
        assert "installments" not in payment_method

    async def test_amount_is_formatted_with_two_decimals(self):
        client = make_client()
        client._http.post = AsyncMock(return_value=_response(200, json_body={}))

        await client.add_transaction("TOKEN", "ORD1", 150, "tok", "visa", "credit_card", 1, "idem-3")

        _, kwargs = client._http.post.call_args
        assert kwargs["json"]["payments"][0]["amount"] == "150.00"

    async def test_error_response_raises(self):
        client = make_client()
        client._http.post = AsyncMock(return_value=_response(409, json_body={"message": "duplicate"}))

        with pytest.raises(httpx.HTTPStatusError):
            await client.add_transaction("TOKEN", "ORD1", 150, "tok", "visa", "credit_card", 1, "idem-4")


class TestProcessOrder:
    async def test_success_returns_json(self):
        client = make_client()
        client._http.post = AsyncMock(
            return_value=_response(200, json_body={"id": "ORD1", "status": "processed"})
        )

        result = await client.process_order("TOKEN", "ORD1", "idem-1")

        assert result == {"id": "ORD1", "status": "processed"}

    async def test_legitimate_rejection_returns_order_data_without_raising(self):
        """MP responde 402 pero el body trae `data` con la orden completa (status
        'failed'): debe devolverse esa orden para que el llamador la mapee a REJECTED,
        no explotar como error interno."""
        client = make_client()
        client._http.post = AsyncMock(
            return_value=_response(
                402,
                json_body={
                    "message": "rejected",
                    "data": {"id": "ORD1", "status": "failed", "status_detail": "cc_rejected_insufficient_amount"},
                },
            )
        )

        result = await client.process_order("TOKEN", "ORD1", "idem-1")

        assert result == {"id": "ORD1", "status": "failed", "status_detail": "cc_rejected_insufficient_amount"}

    async def test_error_without_data_dict_raises(self):
        client = make_client()
        client._http.post = AsyncMock(return_value=_response(400, json_body={"message": "bad_request"}))

        with pytest.raises(httpx.HTTPStatusError):
            await client.process_order("TOKEN", "ORD1", "idem-1")

    async def test_error_with_non_json_body_raises_instead_of_crashing_on_json_decode(self):
        client = make_client()
        client._http.post = AsyncMock(return_value=_response(500, text="<html>Internal Server Error</html>"))

        with pytest.raises(httpx.HTTPStatusError):
            await client.process_order("TOKEN", "ORD1", "idem-1")

    async def test_error_with_data_not_a_dict_raises(self):
        # `data` presente pero no es un dict (ej. lista/string): no matchea el caso de
        # rechazo legitimo, debe propagar el error igual que un 400 comun.
        client = make_client()
        client._http.post = AsyncMock(return_value=_response(400, json_body={"data": "no-es-un-dict"}))

        with pytest.raises(httpx.HTTPStatusError):
            await client.process_order("TOKEN", "ORD1", "idem-1")
