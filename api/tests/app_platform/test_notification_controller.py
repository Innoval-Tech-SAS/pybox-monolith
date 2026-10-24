import uuid

from identity.users.enums.user_enums import UserRole, UserScope

BASE = "/api/v1/notifications"


class TestListNotifications:
    async def test_list_valid(self, auth_as, make_user_session_factory):
        authed = auth_as(
            make_user_session_factory(role=UserRole.USER, scope=UserScope.SELF)
        )
        resp = await authed.get(BASE)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_without_auth_returns_401(self, client):
        resp = await client.get(BASE)
        assert resp.status_code == 401


class TestMarkAllRead:
    async def test_mark_all_read_valid(self, auth_as, make_user_session_factory):
        authed = auth_as(
            make_user_session_factory(role=UserRole.USER, scope=UserScope.SELF)
        )
        resp = await authed.post(f"{BASE}/read-all")
        assert resp.status_code == 204


class TestGetNotification:
    async def test_get_not_found_returns_404(self, auth_as, make_user_session_factory):
        authed = auth_as(
            make_user_session_factory(role=UserRole.USER, scope=UserScope.SELF)
        )
        resp = await authed.get(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404

    async def test_get_without_auth_returns_401(self, client):
        resp = await client.get(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 401


class TestNotificationStream:
    async def test_stream_without_auth_returns_401(self, client):
        resp = await client.get(f"{BASE}/stream")
        assert resp.status_code == 401
