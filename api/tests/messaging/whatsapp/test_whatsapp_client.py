"""Tests unitarios de WhatsAppCloudClient (ver whatsapp_client.py).

`WhatsAppCloudClient` es un singleton (`__new__` con `_instance` compartido entre
todo el proceso de test): en vez de tratar de resetearlo, se reutiliza la misma
instancia y se parcha directo su `_http` (el `httpx.AsyncClient` interno) con un
AsyncMock -- así no se abre ninguna conexión real a la Graph API de Meta.

Foco: los tres métodos de envío/consulta atrapan cualquier excepción (HTTP o de
otro tipo) y no la propagan -- `send_template`/`send_text` devuelven `(False,
None)`, y se verifica explícitamente que el caller nunca ve una excepción.
"""

import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock

from messaging.whatsapp.services.whatsapp_client import WhatsAppCloudClient


@pytest.fixture
def client():
    """`WhatsAppCloudClient` guarda su única instancia en un atributo de CLASE
    (`_instance`), compartida por todo el proceso de test -- mutar `_http`/`_token`
    acá y dejarlo puesto contaminaría cualquier otro test (de este módulo o de
    controllers) que dependa de `get_whatsapp_client()`. Se borra `_instance` al
    salir para que el próximo `WhatsAppCloudClient()` la reconstruya desde cero.
    """
    instance = WhatsAppCloudClient()  # reutiliza el singleton si ya existía
    instance._http = AsyncMock(spec=httpx.AsyncClient)
    instance._token = "test-token"
    instance._waba_id = "waba-123"
    yield instance
    del WhatsAppCloudClient._instance


def _http_response(
    status_code: int, json_body: dict, request: httpx.Request | None = None
) -> httpx.Response:
    request = request or httpx.Request("POST", "https://graph.facebook.com/x")
    return httpx.Response(status_code=status_code, json=json_body, request=request)


class TestSendTemplate:
    async def test_success_returns_true_and_wamid(self, client: WhatsAppCloudClient):
        client._http.request.return_value = _http_response(
            200, {"messages": [{"id": "wamid.123"}]}
        )

        ok, wamid = await client.send_template(
            "phone-id",
            "573000000000",
            "recordatorio_pago",
            "es_CO",
            [{"type": "body", "parameters": []}],
        )

        assert ok is True
        assert wamid == "wamid.123"

    async def test_success_without_messages_in_body_returns_none_wamid(
        self, client: WhatsAppCloudClient
    ):
        client._http.request.return_value = _http_response(200, {"messages": []})

        ok, wamid = await client.send_template(
            "phone-id", "573000000000", "tpl", "es_CO", []
        )

        assert ok is True
        assert wamid is None

    async def test_http_status_error_returns_false_none_without_raising(
        self, client: WhatsAppCloudClient
    ):
        request = httpx.Request("POST", "https://graph.facebook.com/x")
        error_response = httpx.Response(
            status_code=400,
            json={"error": {"message": "Invalid parameter"}},
            request=request,
        )
        client._http.request.return_value = error_response

        ok, wamid = await client.send_template(
            "phone-id", "573000000000", "tpl", "es_CO", []
        )

        assert (ok, wamid) == (False, None)

    async def test_generic_exception_returns_false_none_without_raising(
        self, client: WhatsAppCloudClient
    ):
        client._http.request.side_effect = RuntimeError("boom, red caída")

        ok, wamid = await client.send_template(
            "phone-id", "573000000000", "tpl", "es_CO", []
        )

        assert (ok, wamid) == (False, None)

    async def test_sends_named_parameter_format_and_bearer_token(
        self, client: WhatsAppCloudClient
    ):
        client._http.request.return_value = _http_response(
            200, {"messages": [{"id": "wamid.abc"}]}
        )

        await client.send_template(
            "phone-id",
            "573000000000",
            "recordatorio",
            "es_CO",
            [{"type": "body"}],
            token="org-token",
        )

        call = client._http.request.call_args
        assert call.kwargs["headers"]["Authorization"] == "Bearer org-token"
        assert call.kwargs["json"]["template"]["name"] == "recordatorio"
        assert call.kwargs["json"]["type"] == "template"

    async def test_without_explicit_token_uses_app_level_token(
        self, client: WhatsAppCloudClient
    ):
        client._http.request.return_value = _http_response(
            200, {"messages": [{"id": "wamid.abc"}]}
        )

        await client.send_template("phone-id", "573000000000", "tpl", "es_CO", [])

        call = client._http.request.call_args
        assert call.kwargs["headers"]["Authorization"] == "Bearer test-token"


class TestSendText:
    async def test_success_returns_true_and_wamid(self, client: WhatsAppCloudClient):
        client._http.request.return_value = _http_response(
            200, {"messages": [{"id": "wamid.txt1"}]}
        )

        ok, wamid = await client.send_text(
            "phone-id", "573000000000", "hola, ¿cómo vas?"
        )

        assert (ok, wamid) == (True, "wamid.txt1")
        call = client._http.request.call_args
        assert call.kwargs["json"]["type"] == "text"
        assert call.kwargs["json"]["text"]["body"] == "hola, ¿cómo vas?"

    async def test_http_status_error_returns_false_none(
        self, client: WhatsAppCloudClient
    ):
        request = httpx.Request("POST", "https://graph.facebook.com/x")
        error_response = httpx.Response(
            status_code=403,
            json={"error": {"message": "outside customer service window"}},
            request=request,
        )
        client._http.request.return_value = error_response

        ok, wamid = await client.send_text("phone-id", "573000000000", "hola")

        assert (ok, wamid) == (False, None)

    async def test_generic_exception_returns_false_none(
        self, client: WhatsAppCloudClient
    ):
        client._http.request.side_effect = httpx.ConnectTimeout("timeout")

        ok, wamid = await client.send_text("phone-id", "573000000000", "hola")

        assert (ok, wamid) == (False, None)


class TestCreateTemplate:
    async def test_lowercases_category_and_forces_named_parameter_format(
        self, client: WhatsAppCloudClient
    ):
        client._http.request.return_value = _http_response(
            200, {"id": "meta-tpl-1", "status": "PENDING"}
        )

        result = await client.create_template(
            "recordatorio_pago",
            "UTILITY",
            "es_CO",
            [{"type": "BODY", "text": "Hola {{nombre}}"}],
        )

        assert result == {"id": "meta-tpl-1", "status": "PENDING"}
        call = client._http.request.call_args
        assert call.kwargs["json"]["category"] == "utility"
        assert call.kwargs["json"]["parameter_format"] == "NAMED"

    async def test_http_error_propagates_unlike_send_methods(
        self, client: WhatsAppCloudClient
    ):
        """A diferencia de send_template/send_text, create_template no tiene
        try/except -- un error de Meta debe propagar para que el controller lo
        traduzca en un 5xx/4xx, no quedar silenciado."""
        request = httpx.Request("POST", "https://graph.facebook.com/x")
        error_response = httpx.Response(
            status_code=400, json={"error": {"message": "bad"}}, request=request
        )
        client._http.request.return_value = error_response

        with pytest.raises(httpx.HTTPStatusError):
            await client.create_template("tpl", "UTILITY", "es_CO", [])


class TestGetTemplate:
    async def test_returns_parsed_json(self, client: WhatsAppCloudClient):
        client._http.request.return_value = _http_response(
            200, {"id": "meta-1", "status": "APPROVED"}
        )

        result = await client.get_template("meta-1")

        assert result == {"id": "meta-1", "status": "APPROVED"}


class TestDeleteTemplate:
    async def test_sends_delete_with_name_param(self, client: WhatsAppCloudClient):
        client._http.request.return_value = _http_response(200, {"success": True})

        await client.delete_template("recordatorio_pago")

        call = client._http.request.call_args
        assert call.args[0] == "DELETE"
        assert call.kwargs["params"] == {"name": "recordatorio_pago"}
