from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from core.config.logger import logger
from core.database.database import db
from messaging.campaigns.services.automation_service import tick_now

_running = False


async def _job() -> None:
    global _running
    if _running:
        logger.debug("[campaigns_cron] tick saltado: ejecución previa en curso")
        return
    _running = True
    try:
        async with db.get_session() as session:
            processed = await tick_now(session)
        logger.info("[campaigns_cron] tick: %d campañas procesadas", processed)
    except Exception:
        logger.exception("[campaigns_cron] error en tick")
    finally:
        _running = False


def create_campaigns_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        _job,
        IntervalTrigger(minutes=1),
        id="campaigns_automation",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )
    return scheduler
