import uuid

from identity.organizations.enums.organization_enums import VerificationStatus
from identity.users.enums.user_enums import UserRole, UserScope
from identity.users.schemas.user_session_schema import OrgSessionEntry

BASE = "/api/v1/portfolios"


def other_org_session(make_user_session_factory):
    """Sesión org-scoped admin de una organización DISTINTA a la del portfolio bajo
    prueba -- sirve para los casos 403 sin depender de otro fixture con auth_as."""
    org_id = str(uuid.uuid4())
    return make_user_session_factory(
        role=UserRole.ADMIN,
        scope=UserScope.ORGANIZATION,
        orgs={org_id: OrgSessionEntry(role=UserRole.ADMIN, org_name="Otra org", verification_status=VerificationStatus.APPROVED)},
    )


class TestListPortfolios:
    async def test_valid_as_global_admin(self, auth_as, make_user_session_factory, real_portfolio):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.get(f"{BASE}/", params={"organizationId": str(real_portfolio.organization_id)})
        assert resp.status_code == 200
        assert any(p["id"] == str(real_portfolio.id) for p in resp.json())

    async def test_without_org_membership_returns_403(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.USER, scope=UserScope.SELF))
        resp = await authed.get(f"{BASE}/")
        assert resp.status_code == 403

    async def test_without_auth_returns_401(self, client):
        resp = await client.get(f"{BASE}/")
        assert resp.status_code == 401


class TestGetPortfolio:
    async def test_valid_as_global_admin(self, auth_as, make_user_session_factory, real_portfolio):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.get(f"{BASE}/{real_portfolio.id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == str(real_portfolio.id)

    async def test_not_found_returns_404(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.get(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404

    async def test_forbidden_for_unrelated_org(self, auth_as, make_user_session_factory, real_portfolio):
        authed = auth_as(other_org_session(make_user_session_factory))
        resp = await authed.get(f"{BASE}/{real_portfolio.id}")
        assert resp.status_code == 403


class TestUpdatePortfolio:
    async def test_valid_as_global_admin(self, auth_as, make_user_session_factory, real_portfolio):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.patch(f"{BASE}/{real_portfolio.id}", json={"name": "Nuevo nombre"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Nuevo nombre"

    async def test_not_found_returns_404(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.patch(f"{BASE}/{uuid.uuid4()}", json={"name": "x"})
        assert resp.status_code == 404

    async def test_forbidden_for_unrelated_org(self, auth_as, make_user_session_factory, real_portfolio):
        authed = auth_as(other_org_session(make_user_session_factory))
        resp = await authed.patch(f"{BASE}/{real_portfolio.id}", json={"name": "hack"})
        assert resp.status_code == 403


class TestDeletePortfolio:
    async def test_valid_as_global_admin(self, auth_as, make_user_session_factory, real_portfolio):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.delete(f"{BASE}/{real_portfolio.id}")
        assert resp.status_code == 204
        follow_up = await authed.get(f"{BASE}/{real_portfolio.id}")
        assert follow_up.status_code == 404

    async def test_forbidden_for_unrelated_org(self, auth_as, make_user_session_factory, real_portfolio):
        authed = auth_as(other_org_session(make_user_session_factory))
        resp = await authed.delete(f"{BASE}/{real_portfolio.id}")
        assert resp.status_code == 403


class TestPortfolioStats:
    async def test_valid_as_global_admin(self, auth_as, make_user_session_factory, real_credit):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.get(f"{BASE}/{real_credit.portfolio_id}/stats")
        assert resp.status_code == 200
        body = resp.json()
        assert body["creditos"] == 1
        assert body["titulares"] == 1

    async def test_forbidden_for_unrelated_org(self, auth_as, make_user_session_factory, real_portfolio):
        authed = auth_as(other_org_session(make_user_session_factory))
        resp = await authed.get(f"{BASE}/{real_portfolio.id}/stats")
        assert resp.status_code == 403


class TestPortfolioSendStatusCounts:
    async def test_valid_as_global_admin(self, auth_as, make_user_session_factory, real_portfolio):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.get(f"{BASE}/{real_portfolio.id}/send-status-counts")
        assert resp.status_code == 200


class TestPortfolioMonthlySends:
    async def test_unknown_campaign_returns_404(self, auth_as, make_user_session_factory, real_portfolio):
        # Camino válido (campaña real) diferido a Fase 5 (messaging/campaigns).
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.get(
            f"{BASE}/{real_portfolio.id}/monthly-sends", params={"campaignId": str(uuid.uuid4())}
        )
        assert resp.status_code == 404

    async def test_missing_campaign_id_returns_422(self, auth_as, make_user_session_factory, real_portfolio):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.get(f"{BASE}/{real_portfolio.id}/monthly-sends")
        assert resp.status_code == 422


class TestPortfolioAccess:
    async def test_list_valid_empty(self, auth_as, make_user_session_factory, real_portfolio):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.get(f"{BASE}/{real_portfolio.id}/access")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_replace_access_valid(
        self, client, db_session, auth_as, make_user_session_factory, real_portfolio, real_admin_user_id
    ):
        from tests.factories import get_user_by_email, register_payload

        payload = register_payload()
        resp = await client.post("/api/v1/auth/register/user", json=payload)
        assert resp.status_code == 201
        target_user = await get_user_by_email(db_session, payload["email"])

        authed = auth_as(make_user_session_factory(user_id=real_admin_user_id, role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.put(
            f"{BASE}/{real_portfolio.id}/access", json={"user_ids": [str(target_user.id)]}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 1
        assert body[0]["userId"] == str(target_user.id)
        assert body[0]["isActive"] is True

    async def test_forbidden_for_unrelated_org(self, auth_as, make_user_session_factory, real_portfolio):
        authed = auth_as(other_org_session(make_user_session_factory))
        resp = await authed.get(f"{BASE}/{real_portfolio.id}/access")
        assert resp.status_code == 403


class TestDailyCounterConfig:
    async def test_get_valid_none_when_unconfigured(self, auth_as, make_user_session_factory, real_portfolio):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.get(f"{BASE}/{real_portfolio.id}/daily-counter-config")
        assert resp.status_code == 200
        assert resp.json() is None

    async def test_update_valid(self, auth_as, make_user_session_factory, real_portfolio, real_admin_user_id):
        authed = auth_as(make_user_session_factory(user_id=real_admin_user_id, role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.patch(
            f"{BASE}/{real_portfolio.id}/daily-counter-config", json={"enabled": True}
        )
        assert resp.status_code == 200
        assert resp.json()["enabled"] is True

    async def test_sync_valid(self, auth_as, make_user_session_factory, real_portfolio, real_admin_user_id):
        authed = auth_as(make_user_session_factory(user_id=real_admin_user_id, role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        # sync exige que ya exista una config (404 si no) -- update la crea (upsert).
        await authed.patch(f"{BASE}/{real_portfolio.id}/daily-counter-config", json={"enabled": True})
        resp = await authed.post(f"{BASE}/{real_portfolio.id}/daily-counter-config/sync", json={})
        assert resp.status_code == 200

    async def test_sync_without_existing_config_returns_404(self, auth_as, make_user_session_factory, real_portfolio, real_admin_user_id):
        authed = auth_as(make_user_session_factory(user_id=real_admin_user_id, role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.post(f"{BASE}/{real_portfolio.id}/daily-counter-config/sync", json={})
        assert resp.status_code == 404

    async def test_forbidden_for_unrelated_org(self, auth_as, make_user_session_factory, real_portfolio):
        authed = auth_as(other_org_session(make_user_session_factory))
        resp = await authed.patch(
            f"{BASE}/{real_portfolio.id}/daily-counter-config", json={"enabled": True}
        )
        assert resp.status_code == 403
