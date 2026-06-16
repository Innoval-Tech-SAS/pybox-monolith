from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from config.database_config import db_config
from config.logger import logger
from schema_manager.schemas.database_schemas import AlterAction, ColumnDefinition
from schema_manager.utils.ddl_utils import build_column_ddl, build_column_type, validate_ident


class DdlService:

    def _engine_for(self, db_name: str) -> AsyncEngine:
        validate_ident(db_name, "database name")
        return create_async_engine(
            f"postgresql+asyncpg://{db_config.username}:{db_config.password}"
            f"@{db_config.host}:{db_config.port}/{db_name}"
        )

    async def create_database(self, database_name: str) -> dict[str, Any]:
        validate_ident(database_name, "database name")
        engine = create_async_engine(
            f"postgresql+asyncpg://{db_config.username}:{db_config.password}"
            f"@{db_config.host}:{db_config.port}/postgres",
            isolation_level="AUTOCOMMIT",
        )
        try:
            async with engine.connect() as conn:
                result = await conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :name"),
                    {"name": database_name},
                )
                if result.fetchone():
                    return {"success": False, "message": f"La base de datos '{database_name}' ya existe"}
                await conn.execute(text(f'CREATE DATABASE "{database_name}"'))
                logger.info("[SchemaAlteration] Base de datos creada: %s", database_name)
                return {"success": True, "message": f"Base de datos '{database_name}' creada exitosamente"}
        except Exception as exc:
            logger.error("[SchemaAlteration] Error creando base de datos: %s", exc, exc_info=True)
            return {"success": False, "message": str(exc)}
        finally:
            await engine.dispose()

    async def create_table(
        self,
        database_name: str,
        schema_name: str,
        table_name: str,
        columns: list[ColumnDefinition],
    ) -> dict[str, Any]:
        validate_ident(database_name, "database name")
        validate_ident(schema_name, "schema name")
        validate_ident(table_name, "table name")
        if not columns:
            return {"success": False, "message": "Se debe definir al menos una columna"}
        col_defs = ", ".join(build_column_ddl(c) for c in columns)
        sql = f'CREATE TABLE IF NOT EXISTS "{schema_name}"."{table_name}" ({col_defs})'
        engine = self._engine_for(database_name)
        try:
            async with engine.begin() as conn:
                await conn.execute(text(sql))
            logger.info("[SchemaAlteration] Tabla creada: %s.%s en %s", schema_name, table_name, database_name)
            return {"success": True, "message": f"Tabla '{schema_name}.{table_name}' creada exitosamente"}
        except Exception as exc:
            logger.error("[SchemaAlteration] Error creando tabla: %s", exc, exc_info=True)
            return {"success": False, "message": str(exc)}
        finally:
            await engine.dispose()

    async def alter_table(
        self,
        database_name: str,
        schema_name: str,
        table_name: str,
        action: AlterAction,
        column: ColumnDefinition | None,
        column_name: str | None,
        new_column_name: str | None,
    ) -> dict[str, Any]:
        validate_ident(database_name, "database name")
        validate_ident(schema_name, "schema name")
        validate_ident(table_name, "table name")
        base = f'ALTER TABLE "{schema_name}"."{table_name}"'

        try:
            if action == AlterAction.ADD_COLUMN:
                if column is None:
                    return {"success": False, "message": "Se requiere la definición de columna para ADD_COLUMN"}
                sql = f"{base} ADD COLUMN {build_column_ddl(column)}"

            elif action == AlterAction.DROP_COLUMN:
                if not column_name:
                    return {"success": False, "message": "column_name es requerido para DROP_COLUMN"}
                validate_ident(column_name, "column name")
                sql = f'{base} DROP COLUMN "{column_name}"'

            elif action == AlterAction.MODIFY_COLUMN:
                if not column_name:
                    return {"success": False, "message": "column_name es requerido para MODIFY_COLUMN"}
                if column is None:
                    return {"success": False, "message": "Se requiere la definición de columna para MODIFY_COLUMN"}
                validate_ident(column_name, "column name")
                col_type = build_column_type(column)
                sqls = [
                    f'{base} ALTER COLUMN "{column_name}" TYPE {col_type} USING "{column_name}"::{col_type}',
                    f'{base} ALTER COLUMN "{column_name}" {"SET NOT NULL" if not column.nullable else "DROP NOT NULL"}',
                ]
                if column.default_value:
                    sqls.append(f'{base} ALTER COLUMN "{column_name}" SET DEFAULT {column.default_value}')
                else:
                    sqls.append(f'{base} ALTER COLUMN "{column_name}" DROP DEFAULT')
                engine = self._engine_for(database_name)
                try:
                    async with engine.begin() as conn:
                        for s in sqls:
                            await conn.execute(text(s))
                    logger.info("[SchemaAlteration] Columna modificada: %s en %s.%s", column_name, schema_name, table_name)
                    return {"success": True, "message": f"Columna '{column_name}' modificada exitosamente"}
                except Exception as exc:
                    logger.error("[SchemaAlteration] Error en MODIFY_COLUMN: %s", exc, exc_info=True)
                    return {"success": False, "message": str(exc)}
                finally:
                    await engine.dispose()

            elif action == AlterAction.RENAME_COLUMN:
                if not column_name or not new_column_name:
                    return {"success": False, "message": "column_name y new_column_name son requeridos para RENAME_COLUMN"}
                validate_ident(column_name, "column name")
                validate_ident(new_column_name, "new column name")
                sql = f'{base} RENAME COLUMN "{column_name}" TO "{new_column_name}"'

            else:
                return {"success": False, "message": f"Acción no soportada: {action}"}

        except ValueError as ve:
            return {"success": False, "message": str(ve)}

        engine = self._engine_for(database_name)
        try:
            async with engine.begin() as conn:
                await conn.execute(text(sql))
            logger.info("[SchemaAlteration] ALTER TABLE ejecutado en %s.%s", schema_name, table_name)
            return {"success": True, "message": "Tabla alterada exitosamente"}
        except Exception as exc:
            logger.error("[SchemaAlteration] Error en ALTER TABLE: %s", exc, exc_info=True)
            return {"success": False, "message": str(exc)}
        finally:
            await engine.dispose()
