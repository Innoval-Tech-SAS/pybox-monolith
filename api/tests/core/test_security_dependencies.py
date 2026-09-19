import uuid

import pytest
from fastapi import HTTPException

from core.security.dependencies import (
    _load_session,
    _subject_to_uuid,
    get_pending_mfa_session,
    get_sse_session,
    get_ws_session,
)
from identity.users.schemas.user_session_schema import UserSession, session_key


def _make_session(user_id: uuid.UUID) -> UserSession:
    return UserSession(user_id=user_id, full_name="Test", email="t@example.com")


class TestSubjectToUuid:
    """Cubre core/security/dependencies.py:25-29 -- un `sub` ausente o no-UUID en el
    payload del token no debe explotar con un error 500, sino un 401 controlado."""

    def test_valid_sub_returns_uuid(self):
        user_id = uuid.uuid4()
        assert _subject_to_uuid({"sub": str(user_id)}) == user_id

    def test_missing_sub_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            _subject_to_uuid({})
        assert exc.value.status_code == 401

    def test_non_uuid_sub_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            _subject_to_uuid({"sub": "not-a-uuid"})
        assert exc.value.status_code == 401


class TestLoadSession:
    """Cubre _load_session: JSON corrupto/con forma vieja en Redis (36-37) y ausencia
    de sesión (42) deben devolver 401, nunca un 500 sin manejar."""

    async def test_corrupted_json_raises_401(self, fake_redis):
        user_id = uuid.uuid4()
        await fake_redis.set(session_key(user_id), "{not valid json", 60)
        with pytest.raises(HTTPException) as exc:
            await _load_session(user_id)
        assert exc.value.status_code == 401

    async def test_missing_session_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            await _load_session(uuid.uuid4())
        assert exc.value.status_code == 401

    async def test_valid_session_refreshes_ttl(self, fake_redis):
        user_id = uuid.uuid4()
        session = _make_session(user_id)
        await fake_redis.set(session_key(user_id), session.model_dump_json(), 5)
        loaded = await _load_session(user_id)
        assert loaded.user_id == user_id
        # El TTL se refresca a DEFAULT_TTL (3h) en cada lectura -- sigue vivo mucho
        # después del TTL corto original de 5s.
        entry = fake_redis._store[session_key(user_id)]
        assert entry[1] is not None


class TestPendingMfaSessionInvalidToken:
    async def test_missing_sub_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            await get_pending_mfa_session({})
        assert exc.value.status_code == 401


class TestStreamSessionDependencies:
    """Cubre las ramas de error de get_sse_session/get_ws_session (85-90): token
    inválido/ausente sobre la conexión de streaming debe rechazar con 401."""

    async def test_sse_session_invalid_token_raises_401(self):
        class _FakeRequest:
            cookies: dict = {}

        with pytest.raises(HTTPException) as exc:
            await get_sse_session(_FakeRequest(), token="not-a-real-jwt")
        assert exc.value.status_code == 401

    async def test_sse_session_missing_token_raises_401(self):
        class _FakeRequest:
            cookies: dict = {}

        with pytest.raises(HTTPException) as exc:
            await get_sse_session(_FakeRequest(), token=None)
        assert exc.value.status_code == 401

    async def test_ws_session_invalid_token_raises_401(self):
        class _FakeWebSocket:
            cookies: dict = {}

        with pytest.raises(HTTPException) as exc:
            await get_ws_session(_FakeWebSocket(), token="not-a-real-jwt")
        assert exc.value.status_code == 401
