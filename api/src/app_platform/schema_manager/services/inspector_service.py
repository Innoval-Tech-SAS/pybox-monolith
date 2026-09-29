from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config.logger import logger


class InspectorService:
    """Mismo motivo que DdlService (ver ese docstring) para ejecutar SQL directo:
    lee metadata de `information_schema`/`pg_catalog`, no una entidad de dominio."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_schemas(self) -> list[str]:
        result = await self._session.execute(
            text(
                "SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name != 'information_schema' AND schema_name NOT "
                "LIKE 'pg\\_%' ESCAPE '\\' "
                "ORDER BY schema_name"
            )
        )
        return [row[0] for row in result]

    async def get_tables(self, schema: str) -> list[str]:
        result = await self._session.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = :schema AND table_type = 'BASE TABLE' "
                "ORDER BY table_name"
            ),
            {"schema": schema},
        )
        return [row[0] for row in result]

    async def get_table_fields(self, schema: str, table: str) -> list[dict[str, Any]]:
        # `enum_values` se resuelve en la misma query (subselect correlacionado sobre
        # pg_enum, en orden de declaración) para no hacer un round-trip por columna.
        # Es NULL para toda columna que no sea un enum de PostgreSQL. `data_type` de
        # un enum es "USER-DEFINED": el nombre real del tipo está en
        # udt_name/udt_schema.
        result = await self._session.execute(
            text(
                "SELECT c.column_name AS name, c.data_type AS type, "
                "  (SELECT array_agg(e.enumlabel::text ORDER BY e.enumsortorder) "
                "   FROM pg_type t "
                "   JOIN pg_namespace n ON n.oid = t.typnamespace "
                "   JOIN pg_enum e ON e.enumtypid = t.oid "
                "   WHERE t.typname = c.udt_name AND n.nspname = c.udt_schema) "
                "AS enum_values "
                "FROM information_schema.columns c "
                "WHERE c.table_schema = :schema AND c.table_name = :table "
                "ORDER BY c.ordinal_position"
            ),
            {"schema": schema, "table": table},
        )
        rows = result.fetchall()
        if not rows:
            logger.warning("[Inspector] tabla no encontrada: %s.%s", schema, table)
        return [{"name": row[0], "type": row[1], "enum_values": row[2]} for row in rows]
