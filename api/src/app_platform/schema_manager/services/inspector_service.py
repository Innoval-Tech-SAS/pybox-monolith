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
                "WHERE schema_name != 'information_schema' AND schema_name NOT LIKE 'pg\\_%' ESCAPE '\\' "
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
        result = await self._session.execute(
            text(
                "SELECT column_name AS name, data_type AS type "
                "FROM information_schema.columns "
                "WHERE table_schema = :schema AND table_name = :table "
                "ORDER BY ordinal_position"
            ),
            {"schema": schema, "table": table},
        )
        rows = result.fetchall()
        if not rows:
            logger.warning("[Inspector] tabla no encontrada: %s.%s", schema, table)
        return [{"name": row[0], "type": row[1]} for row in rows]
