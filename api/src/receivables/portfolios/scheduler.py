"""Cron diario de contadores de cartera, uno por zona horaria de país."""

import asyncio
from functools import partial
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.countries.repository.country_repository import CountryRepository
from core.config.logger import logger
from core.database.database import db
from receivables.portfolios.services.daily_counters_service import DailyCountersService


async def _job(country_code: str, tz_str: str) -> None:
    logger.info("[daily_counters] iniciando | país=%s", country_code)
    try:
        async with db.get_session() as session:
            await DailyCountersService(session).run_for_country(country_code, tz_str)
    except asyncio.CancelledError:
        logger.info(
            "[daily_counters] cancelado (apagado en curso) | país=%s", country_code
        )
    except Exception:
        logger.exception("[daily_counters] error | país=%s", country_code)


async def create_daily_counters_scheduler(session: AsyncSession) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    countries = await CountryRepository(session).list_active()
    for country in countries:
        scheduler.add_job(
            partial(_job, country.code, country.timezone),
            CronTrigger(hour=0, minute=5, timezone=ZoneInfo(country.timezone)),
            id=f"daily_counters_{country.code}",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=3600,
        )
    return scheduler
