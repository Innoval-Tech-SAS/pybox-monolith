"""Middleware que loguea método, path, status y duración de cada request."""

import time
from typing import Any, Awaitable, Callable

from core.config.logger import logger

ASGIMessage = dict[str, Any]
Receive = Callable[[], Awaitable[ASGIMessage]]
Send = Callable[[ASGIMessage], Awaitable[None]]


class LoggingMiddleware:
    """ASGI puro, no `starlette.middleware.base.BaseHTTPMiddleware`: esa clase
    intercepta el envío de la respuesta en un stream/task interno, y si el handler
    lanza una excepción no capturada, deja la conexión en un estado que
    `ServerErrorMiddleware` ya no puede usar para mandar la respuesta limpia de
    `@app.exception_handler(Exception)` -- el cliente recibe la conexión cortada
    (`net::ERR_FAILED`) en vez de un 500 con cuerpo JSON. Confirmado leyendo
    `starlette/middleware/errors.py`: `ServerErrorMiddleware` sí arma la respuesta del
    handler registrado, pero solo la envía si `response_started` sigue en `False` --
    con `BaseHTTPMiddleware` de por medio eso dejaba de cumplirse. Un middleware ASGI
    puro no añade ese intermediario: `send_wrapper` solo observa el status, nunca
    retiene ni reordena mensajes."""

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path = scope["path"]
        start = time.perf_counter()
        logger.info("→ %s %s", method, path)
        status_code = 500

        async def send_wrapper(message: ASGIMessage) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            elapsed = int((time.perf_counter() - start) * 1000)
            logger.exception("← 500 %s %s (%dms)", method, path, elapsed)
            raise

        elapsed = int((time.perf_counter() - start) * 1000)
        level = (
            logger.error
            if status_code >= 500
            else logger.warning if status_code >= 400 else logger.info
        )
        level("← %d %s %s (%dms)", status_code, method, path, elapsed)
