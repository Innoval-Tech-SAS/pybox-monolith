from sqlalchemy.exc import DBAPIError

from app_platform.schema_manager.constants.query_constants import (
    DB_ERROR_MESSAGES,
    INVALID_QUERY_STATUS_CODE,
    QUERY_FAILURE_STATUS_CODE,
)


def _postgres_details(exc: DBAPIError) -> tuple[str | None, str]:
    """(SQLSTATE, mensaje del servidor) sin pasar por `str(exc)`: el texto de SQLAlchemy
    trae el SQL completo con el scope de tenant, y eso no debe llegar al cliente.
    SQLAlchemy envuelve el error de asyncpg: el SQLSTATE queda en ambos, el mensaje solo
    en la causa."""
    orig = exc.orig
    cause = getattr(orig, "__cause__", None)
    sqlstate = getattr(orig, "sqlstate", None) or getattr(cause, "sqlstate", None)
    detail = getattr(cause, "message", None) or ""
    return sqlstate, detail


def describe_db_error(exc: DBAPIError) -> tuple[str, int]:
    """Traduce un error de Postgres a (mensaje para el usuario, código HTTP)."""
    sqlstate, detail = _postgres_details(exc)
    base = DB_ERROR_MESSAGES.get(sqlstate or "")
    if base is None:
        suffix = f" (código {sqlstate})" if sqlstate else ""
        return (
            f"Error de base de datos al ejecutar la consulta{suffix}.",
            QUERY_FAILURE_STATUS_CODE,
        )
    return (f"{base} Detalle: {detail}" if detail else base), INVALID_QUERY_STATUS_CODE
