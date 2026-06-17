import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config.logger import logger
from app_platform.schema_manager.constants.query_constants import JOIN_SQL_KEYWORDS, VALID_JOIN_TYPES
from app_platform.schema_manager.utils.query_utils import (
    build_select_parts,
    build_table_alias_map,
    build_where_clauses,
    build_sql_condition,
    is_aggregate_mode,
    normalize_aggregate_specs,
    resolve_alias,
    resolve_full_table_name,
    sanitize_identifier,
    sanitize_table_name,
    serialize_value,
)


class DmlService:

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute_query(
        self,
        tables: list[dict[str, Any]],
        joins: list[dict[str, Any]] | None = None,
        limit: int | None = None,
        query_mode: str = "detail",
        group_by: list[dict[str, Any]] | None = None,
        aggregations: list[dict[str, Any]] | None = None,
        having: list[dict[str, Any]] | None = None,
        order_by: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        try:
            joins = joins or []
            group_by = group_by or []
            aggregations = aggregations or []
            having = having or []
            order_by = order_by or []

            if not tables:
                raise ValueError("At least one table is required")

            aggregate = is_aggregate_mode(query_mode, group_by, aggregations, having, order_by)

            if not aggregate and len(tables) == 1 and not joins:
                return await self._execute_single_table(tables[0], limit)
            if aggregate:
                return await self._execute_aggregate(tables, joins, group_by, aggregations, having, order_by, limit)
            return await self._execute_join(tables, joins, limit)

        except Exception as e:
            logger.error("Error executing dynamic query: %s", e, exc_info=True)
            return {"success": False, "rows": 0, "columns": [], "data": "[]", "error": str(e)}

    async def _execute_single_table(self, table: dict[str, Any], limit: int | None) -> dict[str, Any]:
        try:
            schema, table_name = sanitize_table_name(table["name"])
            alias = sanitize_identifier(table.get("alias") or table_name, label="table alias")
            select_parts = build_select_parts(table, alias)
            query = f"SELECT {', '.join(select_parts)} FROM {schema}.{table_name} AS {alias}"

            where = build_where_clauses(table.get("filters", []), alias)
            if where:
                query += f" WHERE {where}"
            if limit and limit > 0:
                query += f" LIMIT {int(limit)}"

            result = await self._session.execute(text(query))
            rows = result.fetchall()
            columns = list(result.keys())
            data = [{col: serialize_value(val) for col, val in zip(columns, row)} for row in rows]
            return {"success": True, "rows": len(data), "columns": columns, "data": json.dumps(data), "error": ""}
        except Exception as e:
            logger.error("Error in _execute_single_table: %s", e, exc_info=True)
            return {"success": False, "rows": 0, "columns": [], "data": "[]", "error": str(e)}

    async def _execute_join(
        self,
        tables: list[dict[str, Any]],
        joins: list[dict[str, Any]],
        limit: int | None,
    ) -> dict[str, Any]:
        try:
            if len(tables) > 1 and not joins:
                raise ValueError("Joins are required when using multiple tables")

            alias_map = build_table_alias_map(tables)

            select_parts: list[str] = []
            for table in tables:
                schema, table_name = sanitize_table_name(table["name"])
                alias = alias_map[f"{schema}.{table_name}"]
                select_parts.extend(build_select_parts(table, alias, prefixed_alias=True))

            first_schema, first_table = sanitize_table_name(tables[0]["name"])
            first_alias = alias_map[f"{first_schema}.{first_table}"]
            query = f"SELECT {', '.join(select_parts)} FROM {first_schema}.{first_table} AS {first_alias}"

            for join in joins:
                right_schema, right_table = sanitize_table_name(resolve_full_table_name(tables, join["right"]))
                left_alias = resolve_alias(tables, join["left"])
                right_alias = resolve_alias(tables, join["right"])
                left_on = sanitize_identifier(join["left_on"], label="join left_on")
                right_on = sanitize_identifier(join["right_on"], label="join right_on")
                join_type = str(join.get("how", "inner") or "inner").strip().lower()
                if join_type not in VALID_JOIN_TYPES:
                    raise ValueError(f"Invalid join type: {join_type}")
                query += f" {JOIN_SQL_KEYWORDS[join_type]} {right_schema}.{right_table} AS {right_alias}"
                query += f" ON {left_alias}.{left_on} = {right_alias}.{right_on}"

            where_parts: list[str] = []
            for table in tables:
                schema, table_name = sanitize_table_name(table["name"])
                alias = alias_map[f"{schema}.{table_name}"]
                w = build_where_clauses(table.get("filters", []), alias)
                if w:
                    where_parts.append(w)
            if where_parts:
                query += f" WHERE {' AND '.join(where_parts)}"
            if limit and limit > 0:
                query += f" LIMIT {int(limit)}"

            logger.debug("[DmlService] SQL join: %s", query)
            result = await self._session.execute(text(query))
            rows = result.fetchall()
            columns = list(result.keys())
            data = [{col: serialize_value(val) for col, val in zip(columns, row)} for row in rows]
            return {"success": True, "rows": len(data), "columns": columns, "data": json.dumps(data), "error": ""}
        except Exception as e:
            logger.error("Error in _execute_join: %s", e, exc_info=True)
            return {"success": False, "rows": 0, "columns": [], "data": "[]", "error": str(e)}

    async def _execute_aggregate(
        self,
        tables: list[dict[str, Any]],
        joins: list[dict[str, Any]],
        group_by: list[dict[str, Any]],
        aggregations: list[dict[str, Any]],
        having: list[dict[str, Any]],
        order_by: list[dict[str, Any]],
        limit: int | None,
    ) -> dict[str, Any]:
        try:
            if len(tables) > 1 and not joins:
                raise ValueError("Joins are required when multiple tables are configured")

            normalized = normalize_aggregate_specs(tables, group_by, aggregations, having, order_by)
            alias_map = build_table_alias_map(tables)

            first_schema, first_table = sanitize_table_name(tables[0]["name"])
            first_alias = alias_map[f"{first_schema}.{first_table}"]

            select_parts = (
                [f"{g['sql_expression']} AS {g['output_alias']}" for g in normalized["group_by"]]
                + [f"{m['sql_expression']} AS {m['metric_alias']}" for m in normalized["aggregations"]]
            )
            query = f"SELECT {', '.join(select_parts)} FROM {first_schema}.{first_table} AS {first_alias}"

            for join in joins:
                right_schema, right_table = sanitize_table_name(resolve_full_table_name(tables, join["right"]))
                left_alias = resolve_alias(tables, join["left"])
                right_alias = resolve_alias(tables, join["right"])
                left_on = sanitize_identifier(join["left_on"], label="join left_on")
                right_on = sanitize_identifier(join["right_on"], label="join right_on")
                join_type = str(join.get("how", "inner") or "inner").strip().lower()
                if join_type not in VALID_JOIN_TYPES:
                    raise ValueError(f"Invalid join type: {join_type}")
                query += f" {JOIN_SQL_KEYWORDS[join_type]} {right_schema}.{right_table} AS {right_alias}"
                query += f" ON {left_alias}.{left_on} = {right_alias}.{right_on}"

            where_parts2: list[str] = []
            for table in tables:
                schema, table_name = sanitize_table_name(table["name"])
                alias = alias_map[f"{schema}.{table_name}"]
                w = build_where_clauses(table.get("filters", []), alias)
                if w:
                    where_parts2.append(w)
            if where_parts2:
                query += f" WHERE {' AND '.join(where_parts2)}"

            if normalized["group_by"]:
                group_exprs = ", ".join(g["sql_expression"] for g in normalized["group_by"])
                query += f" GROUP BY {group_exprs}"

            if normalized["having"]:
                having_clauses = [
                    build_sql_condition(normalized["metric_sql_by_alias"][h["metric"]], h["op"], h["value"])
                    for h in normalized["having"]
                ]
                query += f" HAVING {' AND '.join(having_clauses)}"

            if normalized["order_by"]:
                order_parts = [f"{o['field']} {o['direction'].upper()}" for o in normalized["order_by"]]
                query += f" ORDER BY {', '.join(order_parts)}"

            if limit and limit > 0:
                query += f" LIMIT {int(limit)}"

            logger.debug("[DmlService] SQL aggregate: %s", query)
            result = await self._session.execute(text(query))
            rows = result.fetchall()
            columns = list(result.keys())
            data = [{col: serialize_value(val) for col, val in zip(columns, row)} for row in rows]
            return {"success": True, "rows": len(data), "columns": columns, "data": json.dumps(data), "error": ""}
        except Exception as e:
            logger.error("Error in _execute_aggregate: %s", e, exc_info=True)
            return {"success": False, "rows": 0, "columns": [], "data": "[]", "error": str(e)}
