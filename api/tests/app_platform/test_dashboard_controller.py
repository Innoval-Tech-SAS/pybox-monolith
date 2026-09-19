import uuid

from identity.organizations.enums.organization_enums import VerificationStatus
from identity.users.enums.user_enums import UserRole, UserScope
from identity.users.schemas.user_session_schema import OrgSessionEntry

BASE = "/api/v1/dashboard"


def org_admin_session(make_user_session_factory, org_id: str):
    return make_user_session_factory(
        role=UserRole.ADMIN,
        scope=UserScope.ORGANIZATION,
        orgs={org_id: OrgSessionEntry(role=UserRole.ADMIN, org_name="Org", verification_status=VerificationStatus.APPROVED)},
    )


class TestOrganizationStats:
    async def test_valid_as_org_admin(self, auth_as, make_user_session_factory):
        org_id = str(uuid.uuid4())
        authed = auth_as(org_admin_session(make_user_session_factory, org_id))
        resp = await authed.get(f"{BASE}/organization-stats", params={"organizationId": org_id})
        assert resp.status_code == 200

    async def test_without_org_admin_returns_403(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.USER, scope=UserScope.SELF))
        resp = await authed.get(f"{BASE}/organization-stats", params={"organizationId": str(uuid.uuid4())})
        assert resp.status_code == 403

    async def test_missing_org_id_returns_422(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.get(f"{BASE}/organization-stats")
        assert resp.status_code == 422


class TestCampaignOptions:
    async def test_valid_as_org_admin(self, auth_as, make_user_session_factory):
        org_id = str(uuid.uuid4())
        authed = auth_as(org_admin_session(make_user_session_factory, org_id))
        resp = await authed.get(f"{BASE}/campaigns", params={"organizationId": org_id})
        assert resp.status_code == 200
        assert resp.json() == []


class TestSendStatusCounts:
    async def test_valid_as_org_admin(self, auth_as, make_user_session_factory):
        org_id = str(uuid.uuid4())
        authed = auth_as(org_admin_session(make_user_session_factory, org_id))
        resp = await authed.get(f"{BASE}/send-status-counts", params={"organizationId": org_id})
        assert resp.status_code == 200


class TestMonthlySends:
    async def test_unknown_campaign_returns_404(self, auth_as, make_user_session_factory):
        # Camino "válido" real (campaña existente) diferido a Fase 5: depende de
        # messaging/campaigns, todavía sin testear.
        org_id = str(uuid.uuid4())
        authed = auth_as(org_admin_session(make_user_session_factory, org_id))
        resp = await authed.get(
            f"{BASE}/monthly-sends", params={"organizationId": org_id, "campaignId": str(uuid.uuid4())}
        )
        assert resp.status_code == 404

    async def test_missing_campaign_id_returns_422(self, auth_as, make_user_session_factory):
        org_id = str(uuid.uuid4())
        authed = auth_as(org_admin_session(make_user_session_factory, org_id))
        resp = await authed.get(f"{BASE}/monthly-sends", params={"organizationId": org_id})
        assert resp.status_code == 422
