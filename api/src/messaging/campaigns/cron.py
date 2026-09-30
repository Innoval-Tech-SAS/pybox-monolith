"""Job periódico que dispara las automatizaciones de campañas vencidas."""

import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from core.config.logger import logger
from core.database.advisory_lock import try_advisory_lock
from core.database.database import db
from messaging.campaigns.services.automation_service import make_automation_service


class _JobState:
    running = False


_state = _JobState()


async def _job() -> None:
    if _state.running:
        logger.debug("[campaigns_cron] tick saltado: ejecución previa en curso")
        return
    _state.running = True
    try:
        async with try_advisory_lock("campaigns_automation") as acquired:
            if not acquired:
                logger.debug(
                    "[campaigns_cron] tick saltado: otro worker ya lo está ejecutando"
                )
                return
            async with db.get_session() as session:
                processed = await make_automation_service(session).tick()
            logger.info("[campaigns_cron] tick: %d campañas procesadas", processed)
    except asyncio.CancelledError:
        # Apagado en curso: el loop/pool de conexiones se están cerrando. Se loguea
        # limpio en vez del traceback de CancelledError y no se re-lanza a propósito
        # (el proceso ya está terminando).
        logger.info("[campaigns_cron] tick cancelado (apagado en curso)")
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("[campaigns_cron] error en tick")
    finally:
        _state.running = False


def create_campaigns_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        _job,
        CronTrigger(minute="*"),
        id="campaigns_automation",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )
    return scheduler
