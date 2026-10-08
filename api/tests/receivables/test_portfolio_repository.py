"""Queries reales de `PortfolioRepository` contra `db_session` (sin mocks)."""

import uuid

from receivables.portfolios.models.portfolio_user_access_model import PortfolioUserAccessModel
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository
from tests.factories import get_user_by_email, register_payload
from tests.receivables.conftest import build_organization, build_portfolio

AUTH_BASE = "/api/v1/auth"


class TestGetByIds:
    async def test_returns_only_matching_non_deleted_portfolios(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        p1 = build_portfolio(org.id)
        p2 = build_portfolio(org.id)
        db_session.add_all([p1, p2])
        await db_session.flush()

        repo = PortfolioRepository(db_session)
        result = await repo.get_by_ids([p1.id, uuid.uuid4()])

        assert {p.id for p in result} == {p1.id}

    async def test_empty_list_returns_empty(self, db_session):
        repo = PortfolioRepository(db_session)
        assert await repo.get_by_ids([]) == []


class TestActiveInactiveByOrganization:
    async def test_get_active_by_organization_id_filters_inactive(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        active = build_portfolio(org.id, is_active=True)
        inactive = build_portfolio(org.id, is_active=False)
        db_session.add_all([active, inactive])
        await db_session.flush()

        repo = PortfolioRepository(db_session)
        result = await repo.get_active_by_organization_id(org.id)

        assert {p.id for p in result} == {active.id}

    async def test_count_active_inactive_by_organization_id(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        db_session.add_all([
            build_portfolio(org.id, is_active=True),
            build_portfolio(org.id, is_active=True),
            build_portfolio(org.id, is_active=False),
        ])
        await db_session.flush()

        repo = PortfolioRepository(db_session)
        active_count, inactive_count = await repo.count_active_inactive_by_organization_id(org.id)

        assert active_count == 2
        assert inactive_count == 1

    async def test_count_for_organization_without_portfolios_is_zero(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()

        repo = PortfolioRepository(db_session)
        active_count, inactive_count = await repo.count_active_inactive_by_organization_id(org.id)

        assert (active_count, inactive_count) == (0, 0)


class TestGetActiveAll:
    async def test_only_returns_active_non_deleted_portfolios(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        active = build_portfolio(org.id, is_active=True)
        inactive = build_portfolio(org.id, is_active=False)
        db_session.add_all([active, inactive])
        await db_session.flush()

        repo = PortfolioRepository(db_session)
        result = await repo.get_active_all()

        ids = {p.id for p in result}
        assert active.id in ids
        assert inactive.id not in ids


class TestListAccessibleByUserAndOrg:
    async def test_only_returns_portfolios_with_active_access_grant(self, client, db_session):
        payload = register_payload()
        resp = await client.post(f"{AUTH_BASE}/register/user", json=payload)
        assert resp.status_code == 201
        user = await get_user_by_email(db_session, payload["email"])

        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        granted = build_portfolio(org.id)
        not_granted = build_portfolio(org.id)
        db_session.add_all([granted, not_granted])
        await db_session.flush()
        db_session.add(PortfolioUserAccessModel(
            user_id=user.id, portfolio_id=granted.id, organization_id=org.id, is_active=True,
        ))
        await db_session.flush()

        repo = PortfolioRepository(db_session)
        result = await repo.list_accessible_by_user_and_org(user.id, org.id)

        assert {p.id for p in result} == {granted.id}

    async def test_revoked_access_is_excluded(self, client, db_session):
        payload = register_payload()
        resp = await client.post(f"{AUTH_BASE}/register/user", json=payload)
        assert resp.status_code == 201
        user = await get_user_by_email(db_session, payload["email"])

        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        db_session.add(PortfolioUserAccessModel(
            user_id=user.id, portfolio_id=portfolio.id, organization_id=org.id, is_active=False,
        ))
        await db_session.flush()

        repo = PortfolioRepository(db_session)
        result = await repo.list_accessible_by_user_and_org(user.id, org.id)

        assert result == []
