from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import case, cast, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import Date as SADate

from core.config.logger import logger
from platform.countries.enums.country_enums import Nationality, NATIONALITY_TIMEZONE
from receivables.credits.models.credit_model import CreditModel
from receivables.portfolios.models.portfolio_daily_counter_config_model import PortfolioDailyCounterConfigModel
from receivables.portfolios.models.portfolio_model import PortfolioModel


async def run_daily_counters_update(session: AsyncSession, nationality: Nationality) -> int:
    tz_str = NATIONALITY_TIMEZONE[nationality]
    tz = ZoneInfo(tz_str)
    today: date = datetime.now(tz).date()
    now = datetime.now(timezone.utc)

    # portfolios habilitados del país
    enabled_portfolios = (
        select(PortfolioDailyCounterConfigModel.portfolio_id)
        .join(PortfolioModel, PortfolioModel.id == PortfolioDailyCounterConfigModel.portfolio_id)
        .where(
            PortfolioDailyCounterConfigModel.enabled.is_(True),
            PortfolioModel.country == nationality,
        )
    )

    mora_condition = or_(
        CreditModel.overdue_principal_balance > 0,
        CreditModel.overdue_installments > 0,
        CreditModel.overdue_interest > 0,
        CreditModel.days_overdue_at_cutoff > 0,
    )

    # court_date convertido a la fecha local del país
    local_court_date = func.timezone(tz_str, CreditModel.court_date).cast(SADate)

    not_updated_today = or_(
        CreditModel.court_date.is_(None),
        local_court_date < today,
    )

    days_delta = case(
        (CreditModel.court_date.is_(None), 1),
        else_=func.greatest(
            cast(today, SADate) - local_court_date,
            0,
        ),
    )

    result = await session.execute(
        update(CreditModel)
        .where(
            CreditModel.portfolio_id.in_(enabled_portfolios),
            mora_condition,
            not_updated_today,
        )
        .values(
            days_overdue_at_cutoff=CreditModel.days_overdue_at_cutoff + days_delta,
            court_date=now,
            updated_at=now,
        )
        .execution_options(synchronize_session=False)
    )
    updated: int = result.rowcount  # type: ignore[union-attr]
    logger.info("[daily_counters] %s (%s) | créditos actualizados=%d", nationality.value, tz_str, updated)
    return updated


async def run_all_nationalities(session: AsyncSession) -> int:
    total = 0
    for nationality in Nationality:
        total += await run_daily_counters_update(session, nationality)
    return total
