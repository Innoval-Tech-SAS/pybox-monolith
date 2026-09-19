"""Tests de `meta_error_to_http_exception` (ver utils/whatsapp_error_utils.py).

Verifica el mapeo de fallos de la Graph API a `HTTPException` con mensaje en español:
credencial rechazada, permisos, rate limit, caída de Meta, rechazo de contenido y red.
"""

import httpx
import pytest

from messaging.whatsapp.constants.whatsapp_constants import (
    META_ERROR_AUTH_MESSAGE,
    META_ERROR_PERMISSION_MESSAGE,
    META_ERROR_RATE_LIMIT_MESSAGE,
    META_ERROR_REJECTED_NO_DETAIL_MESSAGE,
    META_ERROR_UNAVAILABLE_MESSAGE,
    META_ERROR_UNREACHABLE_MESSAGE,
)
from messaging.whatsapp.utils.whatsapp_error_utils import meta_error_to_http_exception


def _status_error(status_code: int, json_body: dict | None = None, text: str | None = None) -> httpx.HTTPStatusError:
    request = httpx.Request("POST", "https://graph.facebook.com/v23.0/waba/message_templates")
    if json_body is not None:
        response = httpx.Response(status_code=status_code, json=json_body, request=request)
    else:
        response = httpx.Response(status_code=status_code, text=text or "", request=request)
    return httpx.HTTPStatusError("error", request=request, response=response)


class TestAuthErrors:
    def test_http_401_maps_to_502_with_token_message(self):
        result = meta_error_to_http_exception(_status_error(401, {"error": {"message": "x", "code": 190}}))
        assert (result.status_code, result.detail) == (502, META_ERROR_AUTH_MESSAGE)

    def test_code_190_with_other_http_status_still_maps_to_auth_message(self):
        result = meta_error_to_http_exception(_status_error(400, {"error": {"code": 190}}))
        assert (result.status_code, result.detail) == (502, META_ERROR_AUTH_MESSAGE)


class TestPermissionAndRateLimit:
    @pytest.mark.parametrize("code", [10, 200, 299])
    def test_permission_codes_map_to_502(self, code):
        result = meta_error_to_http_exception(_status_error(400, {"error": {"code": code}}))
        assert (result.status_code, result.detail) == (502, META_ERROR_PERMISSION_MESSAGE)

    def test_http_403_maps_to_permission_message(self):
        result = meta_error_to_http_exception(_status_error(403, {"error": {}}))
        assert (result.status_code, result.detail) == (502, META_ERROR_PERMISSION_MESSAGE)

    @pytest.mark.parametrize("code", [4, 17, 32, 613, 80007])
    def test_rate_limit_codes_map_to_429(self, code):
        result = meta_error_to_http_exception(_status_error(400, {"error": {"code": code}}))
        assert (result.status_code, result.detail) == (429, META_ERROR_RATE_LIMIT_MESSAGE)

    def test_http_429_maps_to_rate_limit_message(self):
        result = meta_error_to_http_exception(_status_error(429, {"error": {}}))
        assert (result.status_code, result.detail) == (429, META_ERROR_RATE_LIMIT_MESSAGE)


class TestServerAndNetworkErrors:
    def test_meta_5xx_maps_to_502_unavailable(self):
        result = meta_error_to_http_exception(_status_error(503, text="<html>Service Unavailable</html>"))
        assert (result.status_code, result.detail) == (502, META_ERROR_UNAVAILABLE_MESSAGE)

    def test_request_error_maps_to_502_unreachable(self):
        result = meta_error_to_http_exception(httpx.ConnectTimeout("timeout"))
        assert (result.status_code, result.detail) == (502, META_ERROR_UNREACHABLE_MESSAGE)


class TestRejectedContent:
    def test_prefers_user_message_with_title(self):
        body = {"error": {"code": 100, "message": "Invalid parameter", "error_user_title": "Cuerpo inválido", "error_user_msg": "Demasiado largo."}}
        result = meta_error_to_http_exception(_status_error(400, body))
        assert result.status_code == 400
        assert result.detail == "Meta rechazó la solicitud: Cuerpo inválido. Demasiado largo."

    def test_falls_back_to_technical_message(self):
        result = meta_error_to_http_exception(_status_error(400, {"error": {"code": 100, "message": "Invalid parameter"}}))
        assert result.detail == "Meta rechazó la solicitud: Invalid parameter"

    def test_non_json_body_without_detail_uses_generic_rejection(self):
        result = meta_error_to_http_exception(_status_error(400, text="bad request"))
        assert (result.status_code, result.detail) == (400, META_ERROR_REJECTED_NO_DETAIL_MESSAGE)

    def test_detail_is_truncated(self):
        result = meta_error_to_http_exception(_status_error(400, {"error": {"message": "a" * 1000}}))
        assert len(result.detail) < 400
