"""Tests de `NRS360SmsProvider.send_sms` (ver sms_provider.py). Riesgo real: el
payload enviado a 360nrs debe declarar `encoding`/`parts` coherentes con el contenido
real (un mensaje con acentos que se manda como `gsm` se corrompe del lado del
proveedor), y un error HTTP o una excepción inesperada del cliente no deben propagarse
-- el batch sender depende de que esto degrade a `(False, None, None)` en vez de
tumbar el resto del lote.

`NRS360SmsProvider` es un singleton (`__new__`, ver base_provider.py) que lee
`NRS360_SMS_TOKEN`/`NRS360_SMS_SENDER` de entorno al crearse la primera vez -- ya
están en `.env` para todo el resto de la app, así que instanciarlo aquí no requiere
nada extra. Solo se reemplaza `self._http` con un mock, con `patch.object` (se
restaura solo al salir del `with`, indispensable porque la instancia se comparte
entre tests).
"""

import json
from unittest.mock import AsyncMock, patch

import httpx

from messaging.providers.sms_provider import NRS360SmsProvider


def make_response(
    status_code: int = 200, json_body=None, text_body: str = ""
) -> httpx.Response:
    request = httpx.Request("POST", "https://dashboard.360nrs.com/api/rest/sms")
    content = (
        json.dumps(json_body).encode() if json_body is not None else text_body.encode()
    )
    return httpx.Response(status_code=status_code, content=content, request=request)


class TestSendSmsSuccess:
    async def test_returns_ids_by_recipient_and_sending_id(self):
        provider = NRS360SmsProvider()
        response = make_response(
            json_body={
                "result": [{"to": "+573001112233", "id": "ext-1"}],
                "sendingId": 999,
            }
        )
        mock_http = AsyncMock()
        mock_http.request = AsyncMock(return_value=response)

        with patch.object(provider, "_http", mock_http):
            ok, ids_by_recipient, sending_id = await provider.send_sms(
                "hola", ["+573001112233"]
            )

        assert ok is True
        assert ids_by_recipient == {"+573001112233": "ext-1"}
        assert sending_id == "999"

    async def test_recipients_without_id_in_response_are_excluded(self):
        provider = NRS360SmsProvider()
        response = make_response(
            json_body={"result": [{"to": "+573001112233"}], "sendingId": 1}
        )
        mock_http = AsyncMock()
        mock_http.request = AsyncMock(return_value=response)

        with patch.object(provider, "_http", mock_http):
            ok, ids_by_recipient, _ = await provider.send_sms("hola", ["+573001112233"])

        assert ok is True
        assert ids_by_recipient == {}


class TestSendSmsPayload:
    async def test_gsm_safe_message_is_sent_as_gsm_with_one_part(self):
        provider = NRS360SmsProvider()
        response = make_response(json_body={"result": [], "sendingId": 1})
        mock_http = AsyncMock()
        mock_http.request = AsyncMock(return_value=response)

        with patch.object(provider, "_http", mock_http):
            await provider.send_sms(
                "mensaje corto sin acentos",
                ["+573001112233"],
                campaign_name="mi-campana",
            )

        _, kwargs = mock_http.request.call_args
        payload = kwargs["json"]
        assert payload["encoding"] == "gsm"
        assert payload["parts"] == 1
        assert payload["campaignName"] == "mi-campana"

    async def test_message_with_accents_is_sent_as_utf16(self):
        provider = NRS360SmsProvider()
        response = make_response(json_body={"result": [], "sendingId": 1})
        mock_http = AsyncMock()
        mock_http.request = AsyncMock(return_value=response)

        with patch.object(provider, "_http", mock_http):
            await provider.send_sms("Tu crédito está atrasado", ["+573001112233"])

        _, kwargs = mock_http.request.call_args
        assert kwargs["json"]["encoding"] == "utf-16"

    async def test_explicit_credential_overrides_env_token_and_sender(self):
        provider = NRS360SmsProvider()
        response = make_response(json_body={"result": [], "sendingId": 1})
        mock_http = AsyncMock()
        mock_http.request = AsyncMock(return_value=response)

        with patch.object(provider, "_http", mock_http):
            await provider.send_sms(
                "hola", ["+573001112233"], token="Basic pais-override", sender="PAIS"
            )

        _, kwargs = mock_http.request.call_args
        assert kwargs["headers"]["Authorization"] == "Basic pais-override"
        assert kwargs["json"]["from"] == "PAIS"

    async def test_sub_is_included_in_payload_only_when_present(self):
        provider = NRS360SmsProvider()
        response = make_response(json_body={"result": [], "sendingId": 1})
        mock_http = AsyncMock()
        mock_http.request = AsyncMock(return_value=response)

        with patch.object(provider, "_http", mock_http):
            await provider.send_sms("hola", ["+573001112233"])

        _, kwargs = mock_http.request.call_args
        assert "sub" not in kwargs["json"]


class TestSendSmsFailureModes:
    async def test_http_error_status_returns_false_without_raising(self):
        provider = NRS360SmsProvider()
        response = make_response(status_code=500, text_body="internal error")
        mock_http = AsyncMock()
        mock_http.request = AsyncMock(return_value=response)

        with patch.object(provider, "_http", mock_http):
            ok, ids_by_recipient, sending_id = await provider.send_sms(
                "hola", ["+573001112233"]
            )

        assert ok is False
        assert ids_by_recipient is None
        assert sending_id is None

    async def test_unexpected_client_exception_is_caught_and_returns_false(self):
        provider = NRS360SmsProvider()
        mock_http = AsyncMock()
        mock_http.request = AsyncMock(side_effect=RuntimeError("conexión reseteada"))

        with patch.object(provider, "_http", mock_http):
            ok, ids_by_recipient, sending_id = await provider.send_sms(
                "hola", ["+573001112233"]
            )

        assert ok is False
        assert ids_by_recipient is None
        assert sending_id is None
