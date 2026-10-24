"""Convierte cualquier excepción no manejada en una respuesta JSON limpia."""

from fastapi.responses import JSONResponse

from core.config.logger import logger


class ExceptionResponseMiddleware:
    """Debe registrarse ANTES que `CORSMiddleware` en `main.py` (`add_middleware`
    apila de adentro hacia afuera: lo que se agrega primero queda más interno) para
    quedar POR DENTRO de CORS, no por fuera.

    Motivo: Starlette extrae la clave `Exception`/500 de `exception_handlers` y se la
    entrega únicamente a `ServerErrorMiddleware` -- el middleware más externo de
    todos, agregado por fuera de cualquier middleware propio (ver
    `Starlette.build_middleware_stack`). `@app.exception_handler(Exception)`
    (`core/config/error_handlers.py`) nunca lo invoca `ExceptionMiddleware` (el
    interno, junto al ruteo). Cuando `ServerErrorMiddleware` arma esa respuesta de
    emergencia, la manda por el `send` ORIGINAL de ASGI, saltándose por completo el
    `send` envuelto por `CORSMiddleware` -- la respuesta sale sin
    `Access-Control-Allow-Origin` y el navegador la descarta como fallo de CORS
    (`net::ERR_FAILED`, sin cuerpo ni mensaje visible para el usuario).

    Este middleware intercepta la excepción ANTES de salir de `CORSMiddleware`, para
    que la respuesta de error sí reciba esos headers."""

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False

        async def send_wrapper(message: dict) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            logger.exception(
                "Error inesperado en %s %s", scope["method"], scope["path"]
            )
            if not response_started:
                response = JSONResponse(
                    status_code=500, content={"error": "Error interno del servidor"}
                )
                await response(scope, receive, send)
