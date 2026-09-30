"""Job periódico de reconciliación de eventos de envío (SMS/email) con 360NRS."""

import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from core.config.logger import logger
from core.database.advisory_lock import try_advisory_lock
from core.database.database import db
from messaging.results.services.reconciliation_service import (
    make_reconciliation_service,
)


class _JobState:
    running = False


_state = _JobState()


async def _job() -> None:
    if _state.running:
        logger.debug("[results_cron] tick saltado: ejecución previa en curso")
        return
    _state.running = True
    try:
        async with try_advisory_lock("results_reconciliation") as acquired:
            if not acquired:
                logger.debug(
                    "[results_cron] tick saltado: otro worker ya lo está ejecutando"
                )
                return
            async with db.get_session() as session:
                reconciled = await make_reconciliation_service(session).run()
            logger.info("[results_cron] tick: %d sendings reconciliados", reconciled)
    except asyncio.CancelledError:
        logger.info("[results_cron] tick cancelado (apagado en curso)")
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("[results_cron] error en tick")
    finally:
        _state.running = False


def create_results_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        _job,
        CronTrigger(hour="*", minute=0),
        id="results_reconciliation",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=120,
    )
    return scheduler
