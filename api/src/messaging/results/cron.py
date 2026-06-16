from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from core.config.logger import logger
from core.database.database import db
from messaging.results.services.reconciliation_service import make_reconciliation_service

_running = False


async def _job() -> None:
    global _running
    if _running:
        logger.debug("[results_cron] tick saltado: ejecución previa en curso")
        return
    _running = True
    try:
        async with db.get_session() as session:
            reconciled = await make_reconciliation_service(session).run()
        logger.info("[results_cron] tick: %d sendings reconciliados", reconciled)
    except Exception:
        logger.exception("[results_cron] error en tick")
    finally:
        _running = False


def create_results_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        _job,
        CronTrigger(minute="*/5"),
        id="results_reconciliation",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=120,
    )
    return scheduler
