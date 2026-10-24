"""Tests de `NRS360BaseProvider` (cliente HTTP compartido por SMS/Email, ver
base_provider.py). Riesgo real: `get_sending_events_report` es la fuente de datos de
la reconciliación diaria (ver reconciliation_service.py) -- un error HTTP del
proveedor (sending_id vencido, rate limit) no debe tumbar el job, debe degradar a CSV
vacío y dejar que el job siga con el resto de sendings.

`self._http` se reemplaza por un mock -- no hay instancia real de httpx.AsyncClient
hablando por red.
"""

import json
from unittest.mock import AsyncMock

import httpx

from messaging.providers.base_provider import NRS360BaseProvider


class _FakeProvider(NRS360BaseProvider):
    """Subclase mínima -- evita el `__new__` singleton de las subclases reales
    (NRS360SmsProvider/NRS360EmailProvider), que exige tokens de entorno."""

    def __init__(self) -> None:
        self._http = AsyncMock()
        self._token = "test-token"


def make_response(
    status_code: int = 200, json_body=None, text_body: str = ""
) -> httpx.Response:
    request = httpx.Request(
        "GET", "https://dashboard.360nrs.com/api/rest/sendings/x/reports/events"
    )
    content = (
        json.dumps(json_body).encode() if json_body is not None else text_body.encode()
    )
    return httpx.Response(status_code=status_code, content=content, request=request)


class TestRequestSetsAuthorizationHeader:
    async def test_token_is_sent_as_authorization_header(self):
        provider = _FakeProvider()
        provider._http.request = AsyncMock(return_value=make_response())

        await provider._request("GET", "/sendings/x", "Basic abc123")

        _, kwargs = provider._http.request.call_args
        assert kwargs["headers"]["Authorization"] == "Basic abc123"


class TestGetSendingEventsReport:
    async def test_returns_response_body_as_text(self):
        provider = _FakeProvider()
        csv_text = (
            "phone,event,createdAt\n+573001112233,DELIVERED,2026-08-19T10:00:00Z\n"
        )
        provider._http.request = AsyncMock(
            return_value=make_response(text_body=csv_text)
        )

        report = await provider.get_sending_events_report("sending-1")

        assert report == csv_text

    async def test_http_error_returns_empty_string_instead_of_raising(self):
        provider = _FakeProvider()
        provider._http.request = AsyncMock(
            return_value=make_response(status_code=404, text_body="not found")
        )

        report = await provider.get_sending_events_report("sending-vencido")

        assert report == ""

    async def test_optional_date_filters_are_forwarded_as_query_params(self):
        provider = _FakeProvider()
        provider._http.request = AsyncMock(return_value=make_response(text_body=""))

        await provider.get_sending_events_report(
            "sending-1", after_date="2026-08-01", before_date="2026-08-19"
        )

        _, kwargs = provider._http.request.call_args
        assert kwargs["params"] == {
            "afterDate": "2026-08-01",
            "beforeDate": "2026-08-19",
        }

    async def test_no_date_filters_sends_empty_params(self):
        provider = _FakeProvider()
        provider._http.request = AsyncMock(return_value=make_response(text_body=""))

        await provider.get_sending_events_report("sending-1")

        _, kwargs = provider._http.request.call_args
        assert kwargs["params"] == {}


class TestUrl:
    def test_base_url_is_the_nrs360_dashboard(self):
        provider = _FakeProvider()
        assert provider.url == "https://dashboard.360nrs.com/api/rest"
