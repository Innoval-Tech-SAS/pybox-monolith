from sqlalchemy.exc import DBAPIError, IntegrityError, InterfaceError, InternalError

from core.database.database import Database, _is_terminated_connection_error


def _dbapi_error(*, connection_invalidated: bool = False) -> DBAPIError:
    return DBAPIError(
        "SELECT 1", {}, Exception("boom"), connection_invalidated=connection_invalidated
    )


class TestIsTerminatedConnectionError:
    """`_is_terminated_connection_error` decide si un fallo de commit se descarta en
    silencio (conexión ya terminada, típico del apagado) o se re-lanza como un error
    real (p. ej. IntegrityError, que NO invalida la conexión)."""

    def test_connection_invalidated_flag_is_terminated(self):
        assert (
            _is_terminated_connection_error(_dbapi_error(connection_invalidated=True))
            is True
        )

    def test_interface_error_is_terminated(self):
        err = InterfaceError("SELECT 1", {}, Exception("conn gone"))
        assert _is_terminated_connection_error(err) is True

    def test_internal_error_is_terminated(self):
        err = InternalError(
            "SELECT 1", {}, Exception("another operation is in progress")
        )
        assert _is_terminated_connection_error(err) is True

    def test_plain_dbapi_error_without_flag_is_not_terminated(self):
        assert (
            _is_terminated_connection_error(_dbapi_error(connection_invalidated=False))
            is False
        )

    def test_integrity_error_is_not_terminated(self):
        err = IntegrityError("INSERT ...", {}, Exception("duplicate key"))
        assert _is_terminated_connection_error(err) is False


class _FakeSession:
    def __init__(self, commit_error: Exception | None = None) -> None:
        self._commit_error = commit_error
        self.rolled_back = False
        self.closed = False

    async def __aenter__(self) -> "_FakeSession":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False

    async def commit(self) -> None:
        if self._commit_error is not None:
            raise self._commit_error

    async def rollback(self) -> None:
        self.rolled_back = True

    async def close(self) -> None:
        self.closed = True


def _fake_db(session: _FakeSession) -> Database:
    instance = Database.__new__(Database)
    instance._session_factory = lambda: session
    return instance


class TestDatabaseGetSessionCommitHandling:
    """`Database.get_session` descarta en silencio un commit que falla porque la
    conexión ya está terminada (apagado), pero deja propagar cualquier otro error de
    commit -- ver el comentario de `_is_terminated_connection_error`."""

    async def test_terminated_connection_error_is_swallowed(self):
        session = _FakeSession(commit_error=_dbapi_error(connection_invalidated=True))
        database = _fake_db(session)

        async with database.get_session() as s:
            assert s is session

        assert session.rolled_back is True
        assert session.closed is True

    async def test_real_commit_error_propagates(self):
        session = _FakeSession(commit_error=_dbapi_error(connection_invalidated=False))
        database = _fake_db(session)

        raised = False
        try:
            async with database.get_session():
                pass
        except DBAPIError:
            raised = True

        assert raised is True
        assert session.rolled_back is True
        assert session.closed is True

    async def test_exception_inside_block_rolls_back_and_propagates(self):
        session = _FakeSession()
        database = _fake_db(session)

        raised = False
        try:
            async with database.get_session():
                raise ValueError("app error")
        except ValueError:
            raised = True

        assert raised is True
        assert session.rolled_back is True
        assert session.closed is True
