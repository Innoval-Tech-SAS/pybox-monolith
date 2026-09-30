"""Punto de entrada de la API: arma la app FastAPI, middlewares y routers."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Registra los modelos en Base.metadata (mapeos y relaciones).
import core.config.models  # pylint: disable=unused-import
from core.config.error_handlers import register_error_handlers
from core.config.lifespan import lifespan
from core.config.logging_middleware import LoggingMiddleware
from core.config.routers import register_routers
from core.tools.config_tools import get_or_throw

app = FastAPI(
    title="API de Gestión de Cartera",
    description=(
        "Plataforma de administración de portafolios, deudores, créditos y soporte."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_or_throw("CORS_ORIGINS").split(","),
    allow_credentials=True,
    allow_methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Origin",
        "X-Requested-With",
        "Content-Type",
        "Accept",
        "Authorization",
    ],
)

app.add_middleware(LoggingMiddleware)
register_error_handlers(app)

register_routers(app)


@app.get("/")
async def index() -> dict:
    return {"message": "Welcome to the API!"}
