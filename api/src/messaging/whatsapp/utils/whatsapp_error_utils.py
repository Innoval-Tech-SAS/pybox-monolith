from typing import Any

import httpx
from fastapi import HTTPException, status

from core.config.logger import logger
from messaging.whatsapp.constants.whatsapp_constants import (
    META_AUTH_ERROR_CODES,
    META_ERROR_AUTH_MESSAGE,
    META_ERROR_DETAIL_MAX_CHARS,
    META_ERROR_PERMISSION_MESSAGE,
    META_ERROR_RATE_LIMIT_MESSAGE,
    META_ERROR_REJECTED_MESSAGE,
    META_ERROR_REJECTED_NO_DETAIL_MESSAGE,
    META_ERROR_UNAVAILABLE_MESSAGE,
    META_ERROR_UNREACHABLE_MESSAGE,
    META_PERMISSION_ERROR_CODES,
    META_RATE_LIMIT_ERROR_CODES,
)


def _parse_meta_error(response: httpx.Response) -> dict[str, Any]:
    """Extrae el objeto `error` del cuerpo de una respuesta de la Graph API, o `{}` si
    el cuerpo no es JSON o no trae esa forma (ej. una página HTML de un proxy)."""
    try:
        body = response.json()
    except ValueError:
        return {}
    error = body.get("error") if isinstance(body, dict) else None
    return error if isinstance(error, dict) else {}


def _rejection_detail(meta_error: dict[str, Any]) -> str:
    # `error_user_title`/`error_user_msg` son los textos que Meta redacta para el
    # usuario final; `message` es el técnico (en inglés) y queda de respaldo.
    user_msg = meta_error.get("error_user_msg")
    if user_msg:
        user_title = meta_error.get("error_user_title")
        detail = f"{user_title}. {user_msg}" if user_title else str(user_msg)
    else:
        detail = str(meta_error.get("message") or "")
    return detail[:META_ERROR_DETAIL_MAX_CHARS]


def _http_status_to_exception(exc: httpx.HTTPStatusError) -> HTTPException:
    response = exc.response
    meta_error = _parse_meta_error(response)
    code = meta_error.get("code")
    logger.error(
        "[whatsapp] meta_api_error | status=%s code=%s subcode=%s "
        "fbtrace_id=%s message=%s",
        response.status_code,
        code,
        meta_error.get("error_subcode"),
        meta_error.get("fbtrace_id"),
        meta_error.get("message") or response.text[:200],
    )

    if (
        response.status_code == status.HTTP_401_UNAUTHORIZED
        or code in META_AUTH_ERROR_CODES
    ):
        # 502 y no 401: es la credencial de la plataforma ante Meta, no
        # la sesión del usuario, y un 401 propio dispararía el manejo de
        # sesión expirada del cliente.
        return HTTPException(status.HTTP_502_BAD_GATEWAY, META_ERROR_AUTH_MESSAGE)
    if (
        response.status_code == status.HTTP_403_FORBIDDEN
        or code in META_PERMISSION_ERROR_CODES
    ):
        return HTTPException(status.HTTP_502_BAD_GATEWAY, META_ERROR_PERMISSION_MESSAGE)
    if (
        response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        or code in META_RATE_LIMIT_ERROR_CODES
    ):
        return HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS, META_ERROR_RATE_LIMIT_MESSAGE
        )
    if response.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        return HTTPException(
            status.HTTP_502_BAD_GATEWAY, META_ERROR_UNAVAILABLE_MESSAGE
        )

    detail = _rejection_detail(meta_error)
    message = (
        META_ERROR_REJECTED_MESSAGE.format(detail=detail)
        if detail
        else META_ERROR_REJECTED_NO_DETAIL_MESSAGE
    )
    return HTTPException(status.HTTP_400_BAD_REQUEST, message)


def meta_error_to_http_exception(exc: httpx.HTTPError) -> HTTPException:
    """Traduce un fallo de la Graph API (respuesta de error o red caída) a un
    `HTTPException` con mensaje en español para el usuario final."""
    if isinstance(exc, httpx.HTTPStatusError):
        return _http_status_to_exception(exc)
    logger.error(
        "[whatsapp] meta_unreachable | error=%s detail=%s", type(exc).__name__, exc
    )
    return HTTPException(status.HTTP_502_BAD_GATEWAY, META_ERROR_UNREACHABLE_MESSAGE)
