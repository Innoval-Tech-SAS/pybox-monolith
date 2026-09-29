"""Job periódico que cierra las interacciones IVR huérfanas por timeout."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from core.config.logger import logger
from core.database.database import db
from messaging.ivr.services.ivr_stale_service import make_ivr_stale_service


class _JobState:
    running = False


_state = _JobState()


async def _job() -> None:
    if _state.running:
        logger.debug("[ivr_cron] tick saltado: ejecución previa en curso")
        return
    _state.running = True
    try:
        async with db.get_session() as session:
            closed = await make_ivr_stale_service(session).run()
        if closed:
            logger.info(
                "[ivr_cron] tick: %d interacciones cerradas por timeout", closed
            )
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("[ivr_cron] error en tick")
    finally:
        _state.running = False


def create_ivr_scheduler() -> AsyncIOScheduler:
    """Cron de cierre de interacciones huérfanas (cada 10 minutos)."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        _job,
        CronTrigger(minute="*/10"),
        id="ivr_stale_interactions",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=120,
    )
    return scheduler
