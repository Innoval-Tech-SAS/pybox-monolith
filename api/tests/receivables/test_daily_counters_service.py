"""`DailyCountersService.run_for_country`/`run_all_nationalities` con créditos reales
en mora vía `db_session`. El advisory lock en sí ya está cubierto en
`tests/core/test_advisory_lock.py`; aquí importa el efecto sobre los créditos.
"""

from datetime import datetime, timedelta, timezone

from app_platform.countries.repository.country_repository import CountryRepository
from receivables.portfolios.models.portfolio_daily_counter_config_model import PortfolioDailyCounterConfigModel
from receivables.portfolios.services.daily_counters_service import DailyCountersService
from tests.receivables.conftest import build_credit, build_debtor, build_organization, build_portfolio


class TestRunForCountry:
    async def test_advances_overdue_credits_of_enabled_portfolios(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id, country="CO")
        db_session.add(portfolio)
        await db_session.flush()
        db_session.add(PortfolioDailyCounterConfigModel(portfolio_id=portfolio.id, enabled=True))
        debtor = build_debtor()
        db_session.add(debtor)
        await db_session.flush()
        credit = build_credit(
            portfolio.id, debtor.id,
            court_date=None,
            days_overdue_at_cutoff=3,
            overdue_principal_balance=100,
        )
        db_session.add(credit)
        await db_session.flush()

        service = DailyCountersService(db_session)
        updated = await service.run_for_country("CO", "America/Bogota")

        assert updated == 1
        await db_session.refresh(credit)
        assert credit.days_overdue_at_cutoff == 4

    async def test_does_not_touch_credits_without_overdue_signal(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id, country="CO")
        db_session.add(portfolio)
        await db_session.flush()
        db_session.add(PortfolioDailyCounterConfigModel(portfolio_id=portfolio.id, enabled=True))
        debtor = build_debtor()
        db_session.add(debtor)
        await db_session.flush()
        credit = build_credit(
            portfolio.id, debtor.id,
            court_date=None,
            days_overdue_at_cutoff=0,
            overdue_principal_balance=0,
            overdue_installments=0,
            overdue_interest=0,
        )
        db_session.add(credit)
        await db_session.flush()

        service = DailyCountersService(db_session)
        updated = await service.run_for_country("CO", "America/Bogota")

        assert updated == 0
        await db_session.refresh(credit)
        assert credit.days_overdue_at_cutoff == 0

    async def test_other_country_credits_are_not_touched(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id, country="MX")
        db_session.add(portfolio)
        await db_session.flush()
        db_session.add(PortfolioDailyCounterConfigModel(portfolio_id=portfolio.id, enabled=True))
        debtor = build_debtor()
        db_session.add(debtor)
        await db_session.flush()
        credit = build_credit(
            portfolio.id, debtor.id,
            court_date=None,
            days_overdue_at_cutoff=5,
            overdue_principal_balance=100,
        )
        db_session.add(credit)
        await db_session.flush()

        service = DailyCountersService(db_session)
        updated = await service.run_for_country("CO", "America/Bogota")

        assert updated == 0
        await db_session.refresh(credit)
        assert credit.days_overdue_at_cutoff == 5


class TestRunAllNationalities:
    async def test_sums_updates_across_active_countries(self, db_session):
        countries = await CountryRepository(db_session).list_active()
        assert countries, "El seed de países activos debe existir para este test"
        target_country = countries[0]

        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id, country=target_country.code)
        db_session.add(portfolio)
        await db_session.flush()
        db_session.add(PortfolioDailyCounterConfigModel(portfolio_id=portfolio.id, enabled=True))
        debtor = build_debtor()
        db_session.add(debtor)
        await db_session.flush()
        credit = build_credit(
            portfolio.id, debtor.id,
            court_date=None,
            days_overdue_at_cutoff=1,
            overdue_principal_balance=50,
        )
        db_session.add(credit)
        await db_session.flush()

        service = DailyCountersService(db_session)
        total = await service.run_all_nationalities()

        assert total >= 1
        await db_session.refresh(credit)
        assert credit.days_overdue_at_cutoff == 2
