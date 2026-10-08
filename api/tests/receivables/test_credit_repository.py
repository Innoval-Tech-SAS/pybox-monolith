"""Tests unitarios de `CreditRepository` contra la base de datos real (sin mocks):
`db_session` corre en una transacción por test que se revierte sola.

Dos frentes:
- `debtor_belongs_to_portfolio`: la query que respalda el fix del IDOR crítico en
  `DebtorService._require_debtor` (ver test_debtor_service.py) -- se prueba aparte,
  a nivel de repositorio, para blindar el caso soft-delete y el caso sin crédito.
- Cálculos de mora (`bulk_advance_overdue_days`, `get_portfolio_stats`) con números
  concretos: son los puntos donde un off-by-one o un doble conteo pasan
  desapercibidos sin un assert exacto.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from receivables.credits.repository.credit_repository import CreditRepository
from receivables.portfolios.models.portfolio_daily_counter_config_model import PortfolioDailyCounterConfigModel
from tests.receivables.conftest import build_credit, build_debtor, build_organization, build_portfolio

TZ_STR = "America/Bogota"


class TestDebtorBelongsToPortfolio:
    async def test_false_when_credit_is_soft_deleted(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        debtor = build_debtor(org.id)
        db_session.add(debtor)
        await db_session.flush()
        credit = build_credit(portfolio.id, debtor.id, deleted_at=datetime.now(timezone.utc))
        db_session.add(credit)
        await db_session.flush()

        repo = CreditRepository(db_session)
        assert await repo.debtor_belongs_to_portfolio(debtor.id, portfolio.id) is False

    async def test_false_when_debtor_has_no_credit(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        debtor = build_debtor(org.id)
        db_session.add(debtor)
        await db_session.flush()

        repo = CreditRepository(db_session)
        # No debe lanzar excepción -- solo responder False.
        assert await repo.debtor_belongs_to_portfolio(debtor.id, portfolio.id) is False

    async def test_false_when_credit_is_in_a_different_portfolio(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio_x = build_portfolio(org.id)
        portfolio_y = build_portfolio(org.id)
        db_session.add_all([portfolio_x, portfolio_y])
        await db_session.flush()
        debtor = build_debtor(org.id)
        db_session.add(debtor)
        await db_session.flush()
        credit = build_credit(portfolio_x.id, debtor.id)
        db_session.add(credit)
        await db_session.flush()

        repo = CreditRepository(db_session)
        assert await repo.debtor_belongs_to_portfolio(debtor.id, portfolio_y.id) is False


class TestBulkAdvanceOverdueDays:
    async def _setup(self, db_session, *, enabled: bool = True):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id, country="CO")
        db_session.add(portfolio)
        await db_session.flush()
        config = PortfolioDailyCounterConfigModel(portfolio_id=portfolio.id, enabled=enabled)
        db_session.add(config)
        debtor = build_debtor(org.id)
        db_session.add(debtor)
        await db_session.flush()
        return portfolio, debtor

    async def test_credit_with_no_court_date_advances_exactly_one_day(self, db_session):
        portfolio, debtor = await self._setup(db_session, enabled=True)
        credit = build_credit(
            portfolio.id, debtor.id,
            court_date=None,
            days_overdue_at_cutoff=5,
            overdue_principal_balance=100,
        )
        db_session.add(credit)
        await db_session.flush()

        now = datetime.now(timezone.utc)
        today = now.astimezone(ZoneInfo(TZ_STR)).date()

        repo = CreditRepository(db_session)
        updated = await repo.bulk_advance_overdue_days("CO", TZ_STR, today, now)
        assert updated == 1

        await db_session.refresh(credit)
        assert credit.days_overdue_at_cutoff == 6
        assert credit.court_date == now

    async def test_credit_already_updated_today_is_not_modified(self, db_session):
        portfolio, debtor = await self._setup(db_session, enabled=True)
        now = datetime.now(timezone.utc)
        credit = build_credit(
            portfolio.id, debtor.id,
            court_date=now,
            days_overdue_at_cutoff=5,
            overdue_principal_balance=100,
        )
        db_session.add(credit)
        await db_session.flush()

        today = now.astimezone(ZoneInfo(TZ_STR)).date()

        repo = CreditRepository(db_session)
        updated = await repo.bulk_advance_overdue_days("CO", TZ_STR, today, now)
        assert updated == 0

        await db_session.refresh(credit)
        assert credit.days_overdue_at_cutoff == 5
        assert credit.court_date == now

    async def test_credit_in_disabled_portfolio_is_not_touched(self, db_session):
        portfolio, debtor = await self._setup(db_session, enabled=False)
        credit = build_credit(
            portfolio.id, debtor.id,
            court_date=None,
            days_overdue_at_cutoff=5,
            overdue_principal_balance=100,
        )
        db_session.add(credit)
        await db_session.flush()

        now = datetime.now(timezone.utc)
        today = now.astimezone(ZoneInfo(TZ_STR)).date()

        repo = CreditRepository(db_session)
        updated = await repo.bulk_advance_overdue_days("CO", TZ_STR, today, now)
        assert updated == 0

        await db_session.refresh(credit)
        assert credit.days_overdue_at_cutoff == 5
        assert credit.court_date is None


class TestGetByDebtorId:
    async def test_returns_only_credits_where_debtor_is_titular(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        titular = build_debtor(org.id)
        codebtor_only = build_debtor(org.id)
        db_session.add_all([titular, codebtor_only])
        await db_session.flush()
        as_titular = build_credit(portfolio.id, titular.id)
        as_codebtor = build_credit(portfolio.id, codebtor_only.id, codebtor_id=titular.id)
        db_session.add_all([as_titular, as_codebtor])
        await db_session.flush()

        repo = CreditRepository(db_session)
        result = await repo.get_by_debtor_id(titular.id)

        assert {c.id for c in result} == {as_titular.id}

    async def test_excludes_soft_deleted_credits(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        debtor = build_debtor(org.id)
        db_session.add(debtor)
        await db_session.flush()
        credit = build_credit(portfolio.id, debtor.id, deleted_at=datetime.now(timezone.utc))
        db_session.add(credit)
        await db_session.flush()

        repo = CreditRepository(db_session)
        assert await repo.get_by_debtor_id(debtor.id) == []


class TestGetByDebtorAndPortfolio:
    async def test_scopes_credits_to_the_requested_portfolio(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio_a = build_portfolio(org.id)
        portfolio_b = build_portfolio(org.id)
        db_session.add_all([portfolio_a, portfolio_b])
        await db_session.flush()
        debtor = build_debtor(org.id)
        db_session.add(debtor)
        await db_session.flush()
        credit_a = build_credit(portfolio_a.id, debtor.id)
        credit_b = build_credit(portfolio_b.id, debtor.id)
        db_session.add_all([credit_a, credit_b])
        await db_session.flush()

        repo = CreditRepository(db_session)
        result = await repo.get_by_debtor_and_portfolio(debtor.id, portfolio_a.id)

        assert {c.id for c in result} == {credit_a.id}


class TestGetByCodebtorId:
    async def test_returns_only_credits_where_debtor_is_codebtor(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        titular = build_debtor(org.id)
        codebtor = build_debtor(org.id)
        db_session.add_all([titular, codebtor])
        await db_session.flush()
        as_titular = build_credit(portfolio.id, titular.id)
        as_codebtor = build_credit(portfolio.id, titular.id, codebtor_id=codebtor.id)
        db_session.add_all([as_titular, as_codebtor])
        await db_session.flush()

        repo = CreditRepository(db_session)
        result = await repo.get_by_codebtor_id(codebtor.id)

        assert {c.id for c in result} == {as_codebtor.id}


class TestGetLatestByDebtorIds:
    async def test_returns_only_the_most_recently_disbursed_credit_per_debtor(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        debtor = build_debtor(org.id)
        db_session.add(debtor)
        await db_session.flush()
        older = build_credit(portfolio.id, debtor.id, disbursed_date=datetime(2024, 1, 1, tzinfo=timezone.utc))
        newer = build_credit(portfolio.id, debtor.id, disbursed_date=datetime(2025, 1, 1, tzinfo=timezone.utc))
        db_session.add_all([older, newer])
        await db_session.flush()

        repo = CreditRepository(db_session)
        result = await repo.get_latest_by_debtor_ids([debtor.id])

        assert len(result) == 1
        assert result[0].id == newer.id

    async def test_empty_list_returns_empty(self, db_session):
        repo = CreditRepository(db_session)
        assert await repo.get_latest_by_debtor_ids([]) == []


class TestGetPortfolioStats:
    async def test_clientes_unicos_counts_titular_and_codebtor_once(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()

        shared_debtor = build_debtor(org.id)
        other_titular = build_debtor(org.id)
        db_session.add_all([shared_debtor, other_titular])
        await db_session.flush()

        # `shared_debtor` es titular de un crédito Y codeudor de otro, ambos en el
        # MISMO portafolio -- debe contarse una sola vez en `clientes_unicos`.
        db_session.add_all([
            build_credit(portfolio.id, shared_debtor.id),
            build_credit(portfolio.id, other_titular.id, codebtor_id=shared_debtor.id),
        ])
        await db_session.flush()

        repo = CreditRepository(db_session)
        stats = await repo.get_portfolio_stats(portfolio.id)

        assert stats.creditos == 2
        assert stats.titulares == 2
        assert stats.codeudores == 1
        assert stats.clientes_unicos == 2
