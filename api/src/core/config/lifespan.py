"""Ciclo de vida de la app: seeds iniciales, listeners y schedulers en background."""

import asyncio
import contextlib
from contextlib import asynccontextmanager

import redis.exceptions
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from billing.invoices.cron import create_billing_scheduler
from core.config.logger import logger, silence_pool_shutdown_noise
from core.database.database import db
from core.database.schema_version import verify_schema_is_current
from core.database.session_expiry_listener import start_session_expiry_listener
from core.seed import (
    seed_admin,
    seed_channels,
    seed_countries,
    seed_messaging_credentials,
    seed_permissions,
    seed_platform_gateway_credentials,
)
from core.storage.s3_object_storage import object_storage
from messaging.campaigns.cron import create_campaigns_scheduler
from messaging.ivr.cron import create_ivr_scheduler
from messaging.ivr.services.helena_webhook_registrar import ensure_webhook_registered
from messaging.results.cron import create_results_scheduler
from receivables.portfolios.scheduler import create_daily_counters_scheduler
from receivables.portfolios.services.daily_counters_service import DailyCountersService

# Uvicorn arranca varios workers (--workers) que corren este lifespan en paralelo;
# sin este lock, los seeds compiten entre procesos por las mismas filas (duplicate key /
# deadlock en el arranque). El lock serializa el bloque de seed para que solo un worker
# lo ejecute a la vez.
_STARTUP_LOCK_KEY = 727501


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # ── Startup: datos base ──
    # El esquema es responsabilidad de Alembic, no de la app: esto solo ADVIERTE si las
    # migraciones no están al día, no aborta el arranque. Ver
    # core/database/schema_version.py.
    await verify_schema_is_current()

    async with db.engine.connect() as lock_conn:
        await lock_conn.execute(
            text("SELECT pg_advisory_lock(:key)"), {"key": _STARTUP_LOCK_KEY}
        )
        try:
            # Antes que cualquier ruta: si el almacén no responde, es mejor fallar en el
            # arranque que dejar la subida de documentos rompiendo en caliente. Esto NO
            # se relaja: no tiene relación con el esquema de la base.
            await object_storage.startup()
            try:
                async with db.get_session() as session:
                    await seed_countries(session)
                async with db.get_session() as session:
                    await seed_messaging_credentials(session)
                async with db.get_session() as session:
                    await seed_platform_gateway_credentials(session)
                async with db.get_session() as session:
                    await seed_permissions(session)
                async with db.get_session() as session:
                    await seed_admin(session)
                async with db.get_session() as session:
                    await seed_channels(session)
            except SQLAlchemyError as exc:
                # Igual que verify_schema_is_current(): con la base sin migrar, esto
                # revienta con UndefinedTableError. Se advierte y se sigue en vez de
                # tumbar la app — ver core/database/schema_version.py.
                logger.warning(
                    "[lifespan] seed de datos base incompleto "
                    "(¿falta migrar el esquema?): %s",
                    exc,
                )
        finally:
            await lock_conn.execute(
                text("SELECT pg_advisory_unlock(:key)"), {"key": _STARTUP_LOCK_KEY}
            )

    # ── Startup: listeners y schedulers ──
    expiry_task = await start_session_expiry_listener()

    # Igual que el bloque de seeds: create_daily_counters_scheduler() y
    # run_all_nationalities() leen `paises`, así que con la base sin migrar revientan
    # con UndefinedTableError. Se advierte y se sigue sin este scheduler en vez de
    # tumbar la app; queda `None` y el shutdown más abajo lo saltea.
    daily_counters_scheduler = None
    try:
        async with db.get_session() as session:
            daily_counters_scheduler = await create_daily_counters_scheduler(session)
        daily_counters_scheduler.start()
        async with db.get_session() as session:
            await DailyCountersService(session).run_all_nationalities()
    except SQLAlchemyError as exc:
        logger.warning(
            "[lifespan] contadores diarios no inicializados "
            "(¿falta migrar el esquema?): %s",
            exc,
        )

    campaigns_scheduler = create_campaigns_scheduler()
    campaigns_scheduler.start()

    results_scheduler = create_results_scheduler()
    results_scheduler.start()

    billing_scheduler = create_billing_scheduler()
    billing_scheduler.start()

    ivr_scheduler = create_ivr_scheduler()
    ivr_scheduler.start()

    await ensure_webhook_registered()

    yield

    # ── Shutdown ──
    # Al inicio del apagado: la cancelación de los jobs termina conexiones a mitad de
    # query, así que se silencia el ruido del pool antes de detener los schedulers.
    silence_pool_shutdown_noise()
    ivr_scheduler.shutdown(wait=False)
    billing_scheduler.shutdown(wait=False)
    results_scheduler.shutdown(wait=False)
    campaigns_scheduler.shutdown(wait=False)
    if daily_counters_scheduler is not None:
        daily_counters_scheduler.shutdown(wait=False)
    expiry_task.cancel()
    with contextlib.suppress(asyncio.CancelledError, redis.exceptions.RedisError):
        await expiry_task
    await object_storage.shutdown()
    await db.engine.dispose()
