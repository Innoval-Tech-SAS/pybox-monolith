"""Recalcula los contadores diarios de cartera (por país) usados en el dashboard."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.countries.repository.country_repository import CountryRepository
from core.config.logger import logger
from core.database.advisory_lock import try_advisory_lock
from receivables.credits.repository.credit_repository import CreditRepository


class DailyCountersService:
    def __init__(self, session: AsyncSession) -> None:
        self._credit_repo = CreditRepository(session)
        self._country_repo = CountryRepository(session)

    async def run_for_country(self, country_code: str, tz_str: str) -> int:
        # Se llama tanto desde el cron por país (00:05 hora local) como desde el
        # catch-up de arranque (run_all_nationalities): con varios workers de uvicorn,
        # dos procesos pueden pisarse para el mismo país en el mismo instante. El lock
        # vive aquí (y no en cada llamador) para cubrir ambos puntos de entrada con una
        # sola guardia.
        async with try_advisory_lock(f"daily_counters:{country_code}") as acquired:
            if not acquired:
                logger.info(
                    "[daily_counters] %s: saltado, otro worker ya lo está ejecutando",
                    country_code,
                )
                return 0

            tz = ZoneInfo(tz_str)
            today = datetime.now(tz).date()
            now = datetime.now(timezone.utc)

            updated = await self._credit_repo.bulk_advance_overdue_days(
                country_code, tz_str, today, now
            )
            logger.info(
                "[daily_counters] %s (%s) | créditos actualizados=%d",
                country_code,
                tz_str,
                updated,
            )
            return updated

    async def run_all_nationalities(self) -> int:
        total = 0
        countries = await self._country_repo.list_active()
        for country in countries:
            total += await self.run_for_country(country.code, country.timezone)
        return total
