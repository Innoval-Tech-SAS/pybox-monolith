import uuid

from identity.users.enums.user_enums import UserRole, UserScope
from tests.factories import unique_phone

GLOBAL_USERS_BASE = "/api/v1/users/global"
PERMISSIONS_BASE = "/api/v1/permissions"


def global_user_payload(**overrides) -> dict:
    payload = {
        "firstname": "Global",
        "lastname": "User",
        "email": f"global-{uuid.uuid4().hex[:8]}@example.com",
        "phone_number": unique_phone(),
        "password": "Str0ng!Passw0rd",
        "role": "ATENCION_AL_CLIENTE",
    }
    payload.update(overrides)
    return payload


class TestCreateGlobalUser:
    async def test_create_valid_as_global_admin(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.post(GLOBAL_USERS_BASE, json=global_user_payload())
        assert resp.status_code == 201
        assert resp.json()["scope"] == "GLOBAL"

    async def test_create_invalid_role_returns_422(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.post(GLOBAL_USERS_BASE, json=global_user_payload(role="USUARIO"))
        assert resp.status_code == 422

    async def test_create_without_global_admin_returns_403(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.USER, scope=UserScope.SELF))
        resp = await authed.post(GLOBAL_USERS_BASE, json=global_user_payload())
        assert resp.status_code == 403

    async def test_create_without_auth_returns_401(self, client):
        resp = await client.post(GLOBAL_USERS_BASE, json=global_user_payload())
        assert resp.status_code == 401


class TestCreateGlobalAdmin:
    async def test_create_valid_as_global_admin(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        payload = global_user_payload()
        del payload["role"]
        resp = await authed.post(f"{GLOBAL_USERS_BASE}/admin", json=payload)
        assert resp.status_code == 201
        assert resp.json()["role"] == "ADMINISTRADOR"

    async def test_create_missing_field_returns_422(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        payload = global_user_payload()
        del payload["role"]
        del payload["email"]
        resp = await authed.post(f"{GLOBAL_USERS_BASE}/admin", json=payload)
        assert resp.status_code == 422

    async def test_create_without_global_admin_returns_403(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.CUSTOMER_SERVICE, scope=UserScope.GLOBAL))
        payload = global_user_payload()
        del payload["role"]
        resp = await authed.post(f"{GLOBAL_USERS_BASE}/admin", json=payload)
        assert resp.status_code == 403


class TestPermissionsCatalog:
    async def test_list_valid(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.get(PERMISSIONS_BASE)
        assert resp.status_code == 200
        body = resp.json()
        assert any(item["name"] == "portfolio.clients" for item in body)

    async def test_list_without_auth_returns_401(self, client):
        resp = await client.get(PERMISSIONS_BASE)
        assert resp.status_code == 401
