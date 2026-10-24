"""Queries reales de `PortfolioUserAccessRepository` contra `db_session` (sin mocks)."""

from receivables.portfolios.models.portfolio_user_access_model import (
    PortfolioUserAccessModel,
)
from receivables.portfolios.repository.portfolio_user_access_repository import (
    PortfolioUserAccessRepository,
)
from tests.factories import get_user_by_email, register_payload
from tests.receivables.conftest import build_organization, build_portfolio

AUTH_BASE = "/api/v1/auth"


async def create_user(client, db_session):
    payload = register_payload()
    resp = await client.post(f"{AUTH_BASE}/register/user", json=payload)
    assert resp.status_code == 201
    return await get_user_by_email(db_session, payload["email"])


class TestCheckActiveAccess:
    async def test_true_when_active_access_exists(self, client, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        user = await create_user(client, db_session)
        db_session.add(
            PortfolioUserAccessModel(
                user_id=user.id,
                portfolio_id=portfolio.id,
                organization_id=org.id,
                is_active=True,
            )
        )
        await db_session.flush()

        repo = PortfolioUserAccessRepository(db_session)
        assert await repo.check_active_access(user.id, portfolio.id, org.id) is True

    async def test_false_when_access_is_revoked(self, client, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        user = await create_user(client, db_session)
        db_session.add(
            PortfolioUserAccessModel(
                user_id=user.id,
                portfolio_id=portfolio.id,
                organization_id=org.id,
                is_active=False,
            )
        )
        await db_session.flush()

        repo = PortfolioUserAccessRepository(db_session)
        assert await repo.check_active_access(user.id, portfolio.id, org.id) is False

    async def test_false_when_no_record_exists(self, client, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        user = await create_user(client, db_session)

        repo = PortfolioUserAccessRepository(db_session)
        assert await repo.check_active_access(user.id, portfolio.id, org.id) is False


class TestGetDistinctOrgIdsByUser:
    async def test_returns_orgs_with_active_access_only(self, client, db_session):
        org_a = build_organization()
        org_b = build_organization()
        db_session.add_all([org_a, org_b])
        await db_session.flush()
        portfolio_a = build_portfolio(org_a.id)
        portfolio_b = build_portfolio(org_b.id)
        db_session.add_all([portfolio_a, portfolio_b])
        await db_session.flush()
        user = await create_user(client, db_session)
        db_session.add_all(
            [
                PortfolioUserAccessModel(
                    user_id=user.id,
                    portfolio_id=portfolio_a.id,
                    organization_id=org_a.id,
                    is_active=True,
                ),
                PortfolioUserAccessModel(
                    user_id=user.id,
                    portfolio_id=portfolio_b.id,
                    organization_id=org_b.id,
                    is_active=False,
                ),
            ]
        )
        await db_session.flush()

        repo = PortfolioUserAccessRepository(db_session)
        org_ids = await repo.get_distinct_org_ids_by_user(user.id)

        assert org_ids == [org_a.id]


class TestCountActiveUsersForPortfolio:
    async def test_counts_only_active_grants(self, client, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        user_a = await create_user(client, db_session)
        user_b = await create_user(client, db_session)
        db_session.add_all(
            [
                PortfolioUserAccessModel(
                    user_id=user_a.id,
                    portfolio_id=portfolio.id,
                    organization_id=org.id,
                    is_active=True,
                ),
                PortfolioUserAccessModel(
                    user_id=user_b.id,
                    portfolio_id=portfolio.id,
                    organization_id=org.id,
                    is_active=False,
                ),
            ]
        )
        await db_session.flush()

        repo = PortfolioUserAccessRepository(db_session)
        assert await repo.count_active_users_for_portfolio(portfolio.id) == 1

    async def test_zero_when_no_grants_exist(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()

        repo = PortfolioUserAccessRepository(db_session)
        assert await repo.count_active_users_for_portfolio(portfolio.id) == 0


class TestGetActiveUserIdsForPortfolio:
    async def test_returns_only_active_user_ids(self, client, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        user_a = await create_user(client, db_session)
        user_b = await create_user(client, db_session)
        db_session.add_all(
            [
                PortfolioUserAccessModel(
                    user_id=user_a.id,
                    portfolio_id=portfolio.id,
                    organization_id=org.id,
                    is_active=True,
                ),
                PortfolioUserAccessModel(
                    user_id=user_b.id,
                    portfolio_id=portfolio.id,
                    organization_id=org.id,
                    is_active=False,
                ),
            ]
        )
        await db_session.flush()

        repo = PortfolioUserAccessRepository(db_session)
        ids = await repo.get_active_user_ids_for_portfolio(portfolio.id)

        assert ids == [user_a.id]
