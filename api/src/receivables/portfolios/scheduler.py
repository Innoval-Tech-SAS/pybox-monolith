from functools import partial
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from core.config.logger import logger
from app_platform.countries.enums.country_enums import Nationality, NATIONALITY_TIMEZONE
from core.database.database import db
from receivables.portfolios.services.daily_counters_service import run_daily_counters_update


async def _job(nationality: Nationality) -> None:
    logger.info("[daily_counters] iniciando | país=%s", nationality.value)
    try:
        async with db.get_session() as session:
            await run_daily_counters_update(session, nationality)
    except Exception:
        logger.exception("[daily_counters] error | país=%s", nationality.value)


def create_daily_counters_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    for nationality, tz_str in NATIONALITY_TIMEZONE.items():
        scheduler.add_job(
            partial(_job, nationality),
            CronTrigger(hour=0, minute=5, timezone=ZoneInfo(tz_str)),
            id=f"daily_counters_{nationality.value}",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=3600,
        )
    return scheduler
