import uuid

import pytest

from identity.organizations.enums.organization_enums import VerificationStatus
from identity.users.enums.user_enums import UserRole, UserScope
from identity.users.schemas.user_session_schema import OrgSessionEntry
from tests.factories import get_user_by_email, register_payload, unique_phone

AUTH_BASE = "/api/v1/auth"
ORG_BASE = "/api/v1/organizations"


def member_payload(**overrides) -> dict:
    payload = {
        "firstname": "Miembro",
        "lastname": "Test",
        "email": f"member-{uuid.uuid4().hex[:8]}@example.com",
        "phone_number": unique_phone(),
        "password": "Str0ng!Passw0rd",
        "role": "USUARIO",
    }
    payload.update(overrides)
    return payload


@pytest.fixture
async def real_org_id(client, db_session, auth_as, make_user_session_factory) -> str:
    """Crea una organización real usando un admin global respaldado por un
    usuario real (organization_controller refresca la sesión al crear)."""
    payload = register_payload()
    resp = await client.post(f"{AUTH_BASE}/register/user", json=payload)
    assert resp.status_code == 201
    user = await get_user_by_email(db_session, payload["email"])
    global_admin = make_user_session_factory(user_id=user.id, role=UserRole.ADMIN, scope=UserScope.GLOBAL)
    authed = auth_as(global_admin)
    create = await authed.post(f"{ORG_BASE}/", json={"name": f"Org {uuid.uuid4().hex[:8]}", "sector": "FINTECH"})
    assert create.status_code == 201
    auth_as.clear()
    return create.json()["id"]


@pytest.fixture
def base_url(real_org_id: str) -> str:
    return f"{ORG_BASE}/{real_org_id}/members"


@pytest.fixture
async def authed_org_admin(client, db_session, real_org_id, auth_as, make_user_session_factory):
    """Admin de LA organización de `real_org_id`, respaldado por un usuario real:
    `create_org_member` graba `created_by` con FK a `usuarios.id`."""
    payload = register_payload()
    resp = await client.post(f"{AUTH_BASE}/register/user", json=payload)
    assert resp.status_code == 201
    user = await get_user_by_email(db_session, payload["email"])
    session = make_user_session_factory(
        user_id=user.id,
        role=UserRole.ADMIN,
        scope=UserScope.ORGANIZATION,
        orgs={real_org_id: OrgSessionEntry(role=UserRole.ADMIN, org_name="Org", verification_status=VerificationStatus.APPROVED)},
    )
    return auth_as(session)


@pytest.fixture
def non_admin_session(make_user_session_factory, real_org_id):
    return make_user_session_factory(
        role=UserRole.USER,
        scope=UserScope.ORGANIZATION,
        orgs={real_org_id: OrgSessionEntry(role=UserRole.USER, org_name="Org", verification_status=VerificationStatus.APPROVED)},
    )


class TestCreateOrgMember:
    async def test_create_valid(self, authed_org_admin, base_url):
        resp = await authed_org_admin.post(base_url, json=member_payload())
        assert resp.status_code == 201
        body = resp.json()
        assert body["role"] == "USUARIO"

    async def test_create_invalid_role_returns_422(self, authed_org_admin, base_url):
        resp = await authed_org_admin.post(base_url, json=member_payload(role="NOT_A_ROLE"))
        assert resp.status_code == 422

    async def test_create_without_org_admin_returns_403(self, auth_as, non_admin_session, base_url):
        authed = auth_as(non_admin_session)
        resp = await authed.post(base_url, json=member_payload())
        assert resp.status_code == 403

    async def test_create_without_auth_returns_401(self, client, base_url):
        # `real_org_id` registró un usuario real para crear la org: esa cookie de
        # sesión sigue en el jar compartido del client aunque `auth_as` ya se haya
        # limpiado, así que hay que descartarla explícitamente para probar "sin auth".
        client.cookies.clear()
        resp = await client.post(base_url, json=member_payload())
        assert resp.status_code == 401


@pytest.fixture
async def real_member_id(authed_org_admin, base_url) -> str:
    resp = await authed_org_admin.post(base_url, json=member_payload())
    assert resp.status_code == 201
    return resp.json()["id"]


class TestPermissions:
    async def test_list_permissions_valid_empty(self, authed_org_admin, base_url, real_member_id):
        resp = await authed_org_admin.get(f"{base_url}/{real_member_id}/permissions")
        assert resp.status_code == 200
        assert resp.json()["permissions"] == []

    async def test_list_permissions_without_org_admin_returns_403(
        self, auth_as, non_admin_session, base_url, real_member_id
    ):
        authed = auth_as(non_admin_session)
        resp = await authed.get(f"{base_url}/{real_member_id}/permissions")
        assert resp.status_code == 403

    async def test_assign_permission_valid(self, authed_org_admin, base_url, real_member_id):
        resp = await authed_org_admin.put(
            f"{base_url}/{real_member_id}/permissions", json={"name": "portfolio.clients", "effect": "OTORGAR"}
        )
        assert resp.status_code == 200
        assert resp.json() == {"name": "portfolio.clients", "effect": "OTORGAR"}

    async def test_assign_unknown_permission_returns_404(self, authed_org_admin, base_url, real_member_id):
        resp = await authed_org_admin.put(
            f"{base_url}/{real_member_id}/permissions", json={"name": "no.existe", "effect": "OTORGAR"}
        )
        assert resp.status_code == 404

    async def test_assign_permission_invalid_effect_returns_422(self, authed_org_admin, base_url, real_member_id):
        resp = await authed_org_admin.put(
            f"{base_url}/{real_member_id}/permissions", json={"name": "portfolio.clients", "effect": "MAYBE"}
        )
        assert resp.status_code == 422

    async def test_remove_permission_valid(self, authed_org_admin, base_url, real_member_id):
        await authed_org_admin.put(
            f"{base_url}/{real_member_id}/permissions", json={"name": "portfolio.clients", "effect": "OTORGAR"}
        )
        resp = await authed_org_admin.delete(f"{base_url}/{real_member_id}/permissions/portfolio.clients")
        assert resp.status_code == 204

    async def test_remove_permission_not_assigned_returns_404(self, authed_org_admin, base_url, real_member_id):
        resp = await authed_org_admin.delete(f"{base_url}/{real_member_id}/permissions/portfolio.clients")
        assert resp.status_code == 404

    async def test_remove_unknown_permission_returns_404(self, authed_org_admin, base_url, real_member_id):
        resp = await authed_org_admin.delete(f"{base_url}/{real_member_id}/permissions/no.existe")
        assert resp.status_code == 404
