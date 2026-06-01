from typing import Any, Callable, TypeVar

from sqlalchemy import inspect, text
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from config.database_config import DatabaseConfig

T = TypeVar("T")

_db_config = DatabaseConfig()


class DatabaseDescriptorService:

    def _engine_for(self, db_name: str) -> AsyncEngine:
        return create_async_engine(
            f"postgresql+asyncpg://{_db_config.username}:{_db_config.password}"
            f"@{_db_config.host}:{_db_config.port}/{db_name}"
        )

    async def _with_inspector(self, engine: AsyncEngine, fn: Callable[[Inspector], T]) -> T:
        async with engine.begin() as conn:
            return await conn.run_sync(lambda sync_conn: fn(inspect(sync_conn)))

    async def get_databases(self) -> list[str]:
        engine = self._engine_for("postgres")
        try:
            async with engine.begin() as conn:
                def op(sync_conn) -> list[str]:
                    result = sync_conn.execute(
                        text("SELECT datname FROM pg_database WHERE datistemplate = false")
                    )
                    return [row[0] for row in result]
                return await conn.run_sync(op)
        finally:
            await engine.dispose()

    async def get_schemas(self, db_name: str) -> list[str]:
        engine = self._engine_for(db_name)
        try:
            return await self._with_inspector(engine, lambda i: list(i.get_schema_names()))
        finally:
            await engine.dispose()

    async def get_tables(self, db_name: str, schema: str) -> list[str]:
        engine = self._engine_for(db_name)
        try:
            return await self._with_inspector(engine, lambda i: list(i.get_table_names(schema=schema)))
        finally:
            await engine.dispose()

    async def get_table_fields(self, db_name: str, schema: str, table: str) -> list[dict[str, Any]]:
        engine = self._engine_for(db_name)
        try:
            def fn(inspector: Inspector) -> list[dict[str, Any]]:
                if not inspector.has_table(table, schema=schema):
                    return []
                return list(inspector.get_columns(table, schema=schema))
            return await self._with_inspector(engine, fn)
        finally:
            await engine.dispose()
