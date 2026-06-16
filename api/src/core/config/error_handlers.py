from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from core.config.logger import logger
from core.config.validation_messages import ERROR_MESSAGES, FIELD_NAMES

def _format_validation_error(error: dict) -> str:
    error_type: str = error.get("type", "")
    loc: tuple = error.get("loc", ())
    field_key = next((str(l) for l in reversed(loc) if str(l) not in ("body", "query", "path")), "campo")
    field_label = FIELD_NAMES.get(field_key, field_key.replace("_", " "))

    if field_key == "email" or "email" in error.get("msg", "").lower():
        return "El correo electrónico no es válido."

    template = ERROR_MESSAGES.get(error_type)
    if template:
        return template.format(field=field_label)

    return f"El campo '{field_label}' no es válido."


def register_error_handlers(app: FastAPI) -> None:

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        message = _format_validation_error(errors[0]) if errors else "Datos de entrada inválidos."
        return JSONResponse(status_code=422, content={"error": message})

    @app.exception_handler(HTTPException)
    async def handle_http_exception(
        _request: Request, exc: HTTPException
    ) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error("HTTPException %d: %s %s", exc.status_code, _request.method, _request.url.path)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(ValueError)
    async def handle_value_error(
        _request: Request, error: ValueError
    ) -> JSONResponse:
        logger.warning("ValueError en %s %s: %s", _request.method, _request.url.path, error)
        return JSONResponse(status_code=400, content={"error": str(error)})

    @app.exception_handler(RuntimeError)
    async def handle_runtime_error(
        _request: Request, error: RuntimeError
    ) -> JSONResponse:
        logger.warning("RuntimeError en %s %s: %s", _request.method, _request.url.path, error)
        return JSONResponse(status_code=400, content={"error": str(error)})

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        _request: Request, _error: Exception
    ) -> JSONResponse:
        logger.exception("Error inesperado en %s %s", _request.method, _request.url.path)
        return JSONResponse(
            status_code=500, content={"error": "Error interno del servidor"}
        )
