import asyncio
import contextlib
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import core.config.models  # noqa: F401
from core.config.error_handlers import register_error_handlers
from core.config.logging_middleware import LoggingMiddleware
from core.config.paths import UPLOADS_ROOT
from core.config.routers import register_routers
from core.database.database import db
from core.database.session_expiry_listener import start_session_expiry_listener
from messaging.campaigns.cron import create_campaigns_scheduler
from receivables.portfolios.scheduler import create_daily_counters_scheduler
from receivables.portfolios.services.daily_counters_service import run_all_nationalities
from core.security.seed_admin import seed_admin
from core.security.seed_permissions import seed_permissions
from core.tools.config_tools import get_or_throw

os.makedirs(UPLOADS_ROOT, exist_ok=True)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await db.create_tables()
    async with db.get_session() as session:
        await seed_permissions(session)
    async with db.get_session() as session:
        await seed_admin(session)
    expiry_task = await start_session_expiry_listener()

    scheduler = create_daily_counters_scheduler()
    scheduler.start()
    async with db.get_session() as session:
        await run_all_nationalities(session)

    campaigns_scheduler = create_campaigns_scheduler()
    campaigns_scheduler.start()

    yield

    campaigns_scheduler.shutdown(wait=False)
    scheduler.shutdown(wait=False)
    expiry_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await expiry_task
    await db.engine.dispose()


app = FastAPI(
    title="API de Gestión de Cartera",
    description="Plataforma de administración de portafolios, deudores, créditos y soporte.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_or_throw("CORS_ORIGINS").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
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

app.mount("/files", StaticFiles(directory=UPLOADS_ROOT), name="uploads")

register_routers(app)


@app.get("/")
async def index() -> dict:
    return {"message": "Welcome to the API!"}
