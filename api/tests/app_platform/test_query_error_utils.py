"""Unit tests puros (sin DB) del traductor de errores de Postgres del query-builder.

Lo que importa acá es el contrato de seguridad: el mensaje que sale hacia el cliente
nunca contiene el SQL (que incluye el scope de tenant), sea cual sea el error.
"""

from sqlalchemy.exc import DBAPIError

from app_platform.schema_manager.utils.query_error_utils import describe_db_error

SECRET_SQL = "SELECT * FROM public.creditos WHERE id_portafolio IN ('portafolio-secreto')"


class _PgError(Exception):
    """Estandariza el error de asyncpg que SQLAlchemy deja como `__cause__` del `orig`."""


def _db_error(sqlstate: str | None, server_message: str | None = None) -> DBAPIError:
    cause = _PgError(server_message or "")
    cause.sqlstate = sqlstate
    if server_message is not None:
        cause.message = server_message
    orig = Exception(f"<class 'asyncpg.exceptions.X'>: {server_message}")
    orig.sqlstate = sqlstate
    orig.__cause__ = cause
    return DBAPIError(SECRET_SQL, {}, orig)


class TestDescribeDbError:
    def test_undefined_column_is_user_error_with_server_detail(self):
        message, status_code = describe_db_error(_db_error("42703", "column deudores.foo does not exist"))
        assert status_code == 422
        assert "columnas configuradas no existe" in message
        assert "column deudores.foo does not exist" in message

    def test_operator_type_mismatch_is_user_error(self):
        message, status_code = describe_db_error(
            _db_error("42883", "operator does not exist: character varying = bigint")
        )
        assert status_code == 422
        assert "no es compatible con el tipo de dato" in message
        assert "character varying = bigint" in message

    def test_invalid_text_representation_is_user_error(self):
        _, status_code = describe_db_error(_db_error("22P02", 'invalid input syntax for type integer: "abc"'))
        assert status_code == 422

    def test_unmapped_sqlstate_is_server_error_with_code(self):
        message, status_code = describe_db_error(_db_error("40P01", "deadlock detected"))
        assert status_code == 500
        assert "40P01" in message

    def test_missing_sqlstate_is_server_error_without_code(self):
        message, status_code = describe_db_error(_db_error(None))
        assert status_code == 500
        assert "código" not in message

    def test_mapped_error_without_server_message_omits_detail(self):
        message, status_code = describe_db_error(_db_error("22012"))
        assert status_code == 422
        assert message == "La consulta produjo una división por cero."

    def test_sql_never_leaks_into_message(self):
        for sqlstate in ("42703", "42883", "22P02", "40P01", None):
            message, _ = describe_db_error(_db_error(sqlstate, "algún mensaje del servidor"))
            assert "SELECT" not in message
            assert "portafolio-secreto" not in message
