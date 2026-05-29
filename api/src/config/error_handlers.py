from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from config.logger import logger
from contacts.utils.contact_exceptions import DuplicateContactError


def register_error_handlers(app: FastAPI) -> None:

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

    @app.exception_handler(DuplicateContactError)
    async def handle_duplicate_contact(
        _request: Request, error: DuplicateContactError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"error": str(error), "suggestion": error.suggestion},
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
