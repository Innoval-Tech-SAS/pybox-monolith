import asyncio
import uuid
from contextlib import asynccontextmanager
from unittest.mock import patch

from core.database.database import db
from core.database.redis import redis_client
from core.database.session_expiry_listener import _listen_forever, _mark_user_logged_out
from identity.users.models.user_model import UserModel
from identity.users.repository.user_repository import UserRepository
from identity.users.schemas.user_session_schema import session_key
from tests.factories import unique_email, unique_phone


class TestMarkUserLoggedOut:
    """`_mark_user_logged_out` reacciona al evento de expiración `keyevent` de Redis:
    si para cuando el evento se procesa el usuario ya inició sesión de nuevo (la key
    de sesión existe otra vez), NO debe pisar esa sesión activa marcándolo deslogueado.
    """

    async def test_marks_logged_out_when_no_active_session(self, db_session):
        user = await UserRepository(db_session).add(
            UserModel(
                firstname="Ana",
                lastname="Test",
                email=unique_email(),
                phone_number=unique_phone(),
                nationality="CO",
                is_active_sessions=True,
            )
        )

        # `_mark_user_logged_out` abre su PROPIA sesión vía `db.get_session()` (igual
        # que los background tasks) -- se parcha para que sea la misma transacción
        # externa de este test y así el `db_session` del test vea el cambio.
        @asynccontextmanager
        async def _bg_session():
            yield db_session

        original_get_session = db.get_session
        db.get_session = _bg_session
        try:
            await _mark_user_logged_out(user.id)
        finally:
            db.get_session = original_get_session

        assert user.is_active_sessions is False

    async def test_does_not_override_active_session_re_login(self, db_session):
        user_id = uuid.uuid4()
        # Simula un re-login que ocurrió entre la expiración y el procesamiento del
        # evento: la key de sesión ya existe de nuevo.
        await redis_client.set(session_key(user_id), "{}", 60)

        with patch("core.database.session_expiry_listener.UserRepository") as repo_cls:
            await _mark_user_logged_out(user_id)
            # No debe ni siquiera intentar tocar la DB: el recheck corta antes.
            repo_cls.assert_not_called()


class TestListenForever:
    """Si la conexión pub/sub se cae, `_listen_forever` debe reintentar con una
    conexión nueva en vez de dejar morir la tarea en silencio."""

    async def test_retries_after_listen_failure(self, monkeypatch):
        attempts = 0

        async def _flaky_listen(event_client):
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise ConnectionError("pub/sub connection lost")
            raise asyncio.CancelledError()

        monkeypatch.setattr(
            "core.database.session_expiry_listener._listen", _flaky_listen
        )
        monkeypatch.setattr(
            "core.database.session_expiry_listener._RESUBSCRIBE_BACKOFF_SECONDS", 0
        )

        try:
            await _listen_forever()
        except asyncio.CancelledError:
            pass

        assert attempts == 2
