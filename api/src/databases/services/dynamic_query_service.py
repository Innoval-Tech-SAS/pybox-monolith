import json
import re
from decimal import Decimal
from datetime import datetime, date
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config.logger import logger


class DynamicQueryService:

    IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    VALID_WHERE_OPERATORS: set[str] = {
        "=", "!=", "<>", ">", "<", ">=", "<=",
        "in", "not_in", "like", "ilike", "between", "is_null", "is_not_null",
    }
    VALID_HAVING_OPERATORS: set[str] = {
        "=", "!=", "<>", ">", "<", ">=", "<=", "in", "not_in", "between",
    }
    VALID_JOIN_TYPES: set[str] = {"inner", "left", "right", "outer"}
    VALID_AGG_FUNCTIONS: set[str] = {"count", "sum", "avg", "min", "max"}

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value

    def _sanitize_identifier(self, value: str, *, label: str) -> str:
        identifier = str(value or "").strip()
        if not identifier:
            raise ValueError(f"{label} is required")
        if not self.IDENTIFIER_RE.match(identifier):
            raise ValueError(f"Invalid {label}: {value}")
        return identifier

    def _sanitize_table_name(self, full_name: str) -> tuple[str, str]:
        if "." not in str(full_name or ""):
            raise ValueError(f"Table name must include schema: {full_name}")
        schema, table = full_name.split(".", 1)
        return (
            self._sanitize_identifier(schema, label="schema"),
            self._sanitize_identifier(table, label="table"),
        )

    def _normalize_operator(self, op: str) -> str:
        normalized = str(op or "=").strip().lower().replace(" ", "_")
        alias_map = {
            "is_null": "is_null", "is_not_null": "is_not_null",
            "in": "in", "not_in": "not_in", "notin": "not_in",
            "like": "like", "ilike": "ilike", "between": "between",
            "eq": "=", "ne": "!=", "neq": "!=",
            "lt": "<", "lte": "<=", "gt": ">", "gte": ">=",
        }
        return alias_map.get(normalized, normalized)

    def _ensure_operator_allowed(self, op: str, *, in_having: bool = False) -> str:
        normalized = self._normalize_operator(op)
        allowed = self.VALID_HAVING_OPERATORS if in_having else self.VALID_WHERE_OPERATORS
        if normalized not in allowed:
            raise ValueError(f"Invalid operator '{op}'")
        return normalized

    def _normalize_sort_direction(self, direction: str) -> str:
        normalized = str(direction or "asc").strip().lower()
        if normalized not in {"asc", "desc"}:
            raise ValueError(f"Invalid sort direction: {direction}")
        return normalized

    def _normalize_aggregate_function(self, function_name: str) -> str:
        normalized = str(function_name or "").strip().lower()
        if normalized not in self.VALID_AGG_FUNCTIONS:
            raise ValueError(f"Unsupported aggregation function: {function_name}")
        return normalized

    def _parse_json_if_string(self, value: Any) -> Any:
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (TypeError, ValueError):
                return value
        return value

    def _sql_literal(self, value: Any) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, (datetime, date)):
            return f"'{value.isoformat()}'"
        if isinstance(value, Decimal):
            return str(float(value))
        if isinstance(value, bytes):
            escaped = value.decode("utf-8", errors="ignore").replace("'", "''")
            return f"'{escaped}'"
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"

    def _build_sql_condition(self, expression: str, operator: str, value: Any) -> str:
        if operator == "is_null":
            return f"{expression} IS NULL"
        if operator == "is_not_null":
            return f"{expression} IS NOT NULL"
        if operator == "in":
            values = value if isinstance(value, list) else [value]
            if not values:
                raise ValueError("IN operator requires at least one value")
            values_str = ", ".join(self._sql_literal(v) for v in values)
            return f"{expression} IN ({values_str})"
        if operator == "not_in":
            values = value if isinstance(value, list) else [value]
            if not values:
                raise ValueError("NOT IN operator requires at least one value")
            values_str = ", ".join(self._sql_literal(v) for v in values)
            return f"{expression} NOT IN ({values_str})"
        if operator == "between":
            values = value if isinstance(value, list) else []
            if len(values) != 2:
                raise ValueError("BETWEEN operator requires exactly two values")
            return f"{expression} BETWEEN {self._sql_literal(values[0])} AND {self._sql_literal(values[1])}"
        if operator == "like":
            return f"{expression} LIKE {self._sql_literal(value)}"
        if operator == "ilike":
            return f"{expression} ILIKE {self._sql_literal(value)}"
        sql_operator = "<>" if operator == "!=" else operator
        return f"{expression} {sql_operator} {self._sql_literal(value)}"

    def _build_where_clauses(self, filters: list[dict[str, Any]], alias: str) -> str:
        if not filters:
            return ""
        clauses = []
        for f in filters:
            column = self._sanitize_identifier(f["column"], label="filter column")
            op = self._ensure_operator_allowed(f.get("op", "="), in_having=False)
            value = self._parse_json_if_string(f.get("value"))
            qualified = f"{alias}.{column}"
            clauses.append(self._build_sql_condition(qualified, op, value))
        return " AND ".join(clauses)

    def _build_table_alias_map(self, tables: list[dict[str, Any]]) -> dict[str, str]:
        alias_map: dict[str, str] = {}
        alias_set: set[str] = set()
        for table in tables:
            schema, table_name = self._sanitize_table_name(table["name"])
            full_name = f"{schema}.{table_name}"
            alias = table.get("alias") or table_name
            alias = self._sanitize_identifier(alias, label=f"alias for {full_name}")
            if alias in alias_set:
                raise ValueError(f"Duplicate table alias: {alias}")
            alias_set.add(alias)
            alias_map[full_name] = alias
        return alias_map

    def _resolve_alias(self, tables: list[dict[str, Any]], table_ref: str | None) -> str:
        alias_map = self._build_table_alias_map(tables)
        if not table_ref:
            if len(alias_map) == 1:
                return next(iter(alias_map.values()))
            raise ValueError("Table reference is required when multiple tables are used")
        ref = str(table_ref).strip()
        if ref in alias_map.values():
            return self._sanitize_identifier(ref, label="table alias")
        schema, table = self._sanitize_table_name(ref)
        full_name = f"{schema}.{table}"
        if full_name not in alias_map:
            raise ValueError(f"Unknown table reference: {table_ref}")
        return alias_map[full_name]

    def _resolve_full_table_name(self, tables: list[dict[str, Any]], table_ref: str | None) -> str:
        alias_map = self._build_table_alias_map(tables)
        if not table_ref:
            if len(alias_map) == 1:
                return next(iter(alias_map.keys()))
            raise ValueError("Table reference is required when multiple tables are used")
        ref = str(table_ref).strip()
        if ref in alias_map:
            return ref
        for full_name, alias in alias_map.items():
            if alias == ref:
                return full_name
        schema, table = self._sanitize_table_name(ref)
        full_name = f"{schema}.{table}"
        if full_name not in alias_map:
            raise ValueError(f"Unknown table reference: {table_ref}")
        return full_name

    def _build_select_parts(
        self,
        table: dict[str, Any],
        alias: str,
        *,
        prefixed_alias: bool = False,
    ) -> list[str]:
        columns = table.get("columns") or []
        if not columns:
            return [f"{alias}.*"]
        parts = []
        for raw_col in columns:
            col = self._sanitize_identifier(raw_col, label="column")
            if prefixed_alias:
                parts.append(f"{alias}.{col} AS {alias}_{col}")
            else:
                parts.append(f"{alias}.{col}")
        return parts

    def _default_group_alias(self, alias_value: str | None, column: str) -> str:
        if alias_value:
            return self._sanitize_identifier(alias_value, label="group alias")
        return self._sanitize_identifier(column, label="group column")

    def _default_aggregation_alias(self, function_name: str, column: str, table_alias: str) -> str:
        fn = self._normalize_aggregate_function(function_name)
        if column == "*":
            return f"{fn}_all"
        safe_col = self._sanitize_identifier(column, label="aggregation column")
        safe_alias = self._sanitize_identifier(table_alias, label="table alias")
        return f"{fn}_{safe_alias}_{safe_col}"

    def _normalize_aggregate_specs(
        self,
        tables: list[dict[str, Any]],
        group_by: list[dict[str, Any]],
        aggregations: list[dict[str, Any]],
        having: list[dict[str, Any]],
        order_by: list[dict[str, Any]],
    ) -> dict[str, Any]:
        alias_map = self._build_table_alias_map(tables)
        output_aliases: set[str] = set()
        group_aliases: set[str] = set()
        metric_aliases: set[str] = set()
        metric_sql_by_alias: dict[str, str] = {}

        normalized_group_by: list[dict[str, Any]] = []
        for group in group_by:
            table_alias = self._resolve_alias(tables, group.get("table"))
            column = self._sanitize_identifier(group.get("column"), label="group_by column")
            output_alias = self._default_group_alias(group.get("alias"), column)
            if output_alias in output_aliases:
                raise ValueError(f"Duplicated output alias: {output_alias}")
            output_aliases.add(output_alias)
            group_aliases.add(output_alias)
            normalized_group_by.append({
                "table_alias": table_alias,
                "column": column,
                "output_alias": output_alias,
                "sql_expression": f"{table_alias}.{column}",
            })

        if not aggregations:
            raise ValueError("At least one aggregation is required in aggregate mode")

        default_single_alias = next(iter(alias_map.values())) if len(alias_map) == 1 else None

        normalized_aggregations: list[dict[str, Any]] = []
        for metric in aggregations:
            fn = self._normalize_aggregate_function(metric.get("function"))
            raw_col = str(metric.get("column") or "").strip()
            if not raw_col:
                raise ValueError("Aggregation column is required")

            if raw_col == "*":
                if fn != "count":
                    raise ValueError("Only COUNT supports column='*'")
                table_alias = self._resolve_alias(tables, metric.get("table")) if metric.get("table") else default_single_alias
                sql_expression = "COUNT(*)"
            else:
                table_alias = self._resolve_alias(tables, metric.get("table"))
                col = self._sanitize_identifier(raw_col, label="aggregation column")
                sql_expression = f"{fn.upper()}({table_alias}.{col})"

            metric_alias = metric.get("alias") or self._default_aggregation_alias(fn, raw_col, table_alias or "all")
            metric_alias = self._sanitize_identifier(metric_alias, label="aggregation alias")
            if metric_alias in output_aliases:
                raise ValueError(f"Duplicated output alias: {metric_alias}")
            output_aliases.add(metric_alias)
            metric_aliases.add(metric_alias)
            metric_sql_by_alias[metric_alias] = sql_expression
            normalized_aggregations.append({
                "function": fn,
                "table_alias": table_alias,
                "column": raw_col,
                "metric_alias": metric_alias,
                "sql_expression": sql_expression,
            })

        normalized_having: list[dict[str, Any]] = []
        for condition in having:
            metric_alias = self._sanitize_identifier(condition.get("metric"), label="having metric")
            if metric_alias not in metric_aliases:
                raise ValueError(f"Unknown metric alias in HAVING: {metric_alias}")
            op = self._ensure_operator_allowed(condition.get("op", "="), in_having=True)
            value = self._parse_json_if_string(condition.get("value"))
            normalized_having.append({"metric": metric_alias, "op": op, "value": value})

        sortable_fields = group_aliases | metric_aliases
        normalized_order_by: list[dict[str, Any]] = []
        for ordering in order_by:
            field = self._sanitize_identifier(ordering.get("field"), label="order_by field")
            if field not in sortable_fields:
                raise ValueError(f"order_by field '{field}' must reference a group_by or aggregation alias")
            direction = self._normalize_sort_direction(ordering.get("direction", "asc"))
            normalized_order_by.append({"field": field, "direction": direction})

        return {
            "group_by": normalized_group_by,
            "aggregations": normalized_aggregations,
            "having": normalized_having,
            "order_by": normalized_order_by,
            "metric_sql_by_alias": metric_sql_by_alias,
        }

    def _is_aggregate_mode(
        self,
        query_mode: str,
        group_by: list[dict[str, Any]],
        aggregations: list[dict[str, Any]],
        having: list[dict[str, Any]],
        order_by: list[dict[str, Any]],
    ) -> bool:
        if str(query_mode or "").strip().lower() == "aggregate":
            return True
        return bool(group_by or aggregations or having or order_by)

    async def execute_query(
        self,
        tables: list[dict[str, Any]],
        joins: list[dict[str, Any]] | None = None,
        limit: int = 1000,
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

            is_aggregate = self._is_aggregate_mode(query_mode, group_by, aggregations, having, order_by)

            if not is_aggregate and len(tables) == 1 and not joins:
                return await self._execute_single_table(tables[0], limit)

            if is_aggregate:
                return await self._execute_aggregate(tables, joins, group_by, aggregations, having, order_by, limit)

            return await self._execute_join(tables, joins, limit)

        except Exception as e:
            logger.error("Error executing dynamic query: %s", e, exc_info=True)
            return {"success": False, "rows": 0, "columns": [], "data": "[]", "error": str(e)}

    async def _execute_single_table(self, table: dict[str, Any], limit: int) -> dict[str, Any]:
        try:
            schema, table_name = self._sanitize_table_name(table["name"])
            alias = table.get("alias") or table_name
            alias = self._sanitize_identifier(alias, label="table alias")
            select_parts = self._build_select_parts(table, alias)
            query = f"SELECT {', '.join(select_parts)} FROM {schema}.{table_name} AS {alias}"

            where = self._build_where_clauses(table.get("filters", []), alias)
            if where:
                query += f" WHERE {where}"
            if limit and limit > 0:
                query += f" LIMIT {int(limit)}"

            result = await self._session.execute(text(query))
            rows = result.fetchall()
            columns = list(result.keys())
            data = [{col: self._serialize_value(val) for col, val in zip(columns, row)} for row in rows]
            return {"success": True, "rows": len(data), "columns": columns, "data": json.dumps(data), "error": ""}
        except Exception as e:
            logger.error("Error in _execute_single_table: %s", e, exc_info=True)
            return {"success": False, "rows": 0, "columns": [], "data": "[]", "error": str(e)}

    async def _execute_join(
        self,
        tables: list[dict[str, Any]],
        joins: list[dict[str, Any]],
        limit: int,
    ) -> dict[str, Any]:
        try:
            if len(tables) > 1 and not joins:
                raise ValueError("Joins are required when using multiple tables")

            alias_map = self._build_table_alias_map(tables)

            select_parts: list[str] = []
            for table in tables:
                schema, table_name = self._sanitize_table_name(table["name"])
                alias = alias_map[f"{schema}.{table_name}"]
                select_parts.extend(self._build_select_parts(table, alias, prefixed_alias=True))

            first_schema, first_table = self._sanitize_table_name(tables[0]["name"])
            first_alias = alias_map[f"{first_schema}.{first_table}"]
            query = f"SELECT {', '.join(select_parts)} FROM {first_schema}.{first_table} AS {first_alias}"

            for join in joins:
                right_schema, right_table = self._sanitize_table_name(join["right"])
                left_alias = self._resolve_alias(tables, join["left"])
                right_alias = self._resolve_alias(tables, join["right"])
                left_on = self._sanitize_identifier(join["left_on"], label="join left_on")
                right_on = self._sanitize_identifier(join["right_on"], label="join right_on")
                join_type = str(join.get("how", "inner") or "inner").strip().lower()
                if join_type not in self.VALID_JOIN_TYPES:
                    raise ValueError(f"Invalid join type: {join_type}")
                query += f" {join_type.upper()} JOIN {right_schema}.{right_table} AS {right_alias}"
                query += f" ON {left_alias}.{left_on} = {right_alias}.{right_on}"

            where_parts: list[str] = []
            for table in tables:
                schema, table_name = self._sanitize_table_name(table["name"])
                alias = alias_map[f"{schema}.{table_name}"]
                w = self._build_where_clauses(table.get("filters", []), alias)
                if w:
                    where_parts.append(w)
            if where_parts:
                query += f" WHERE {' AND '.join(where_parts)}"

            if limit and limit > 0:
                query += f" LIMIT {int(limit)}"

            logger.debug("[DynamicQuery] SQL: %s", query)
            result = await self._session.execute(text(query))
            rows = result.fetchall()
            columns = list(result.keys())
            data = [{col: self._serialize_value(val) for col, val in zip(columns, row)} for row in rows]
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
        limit: int,
    ) -> dict[str, Any]:
        try:
            if len(tables) > 1 and not joins:
                raise ValueError("Joins are required when multiple tables are configured")

            normalized = self._normalize_aggregate_specs(tables, group_by, aggregations, having, order_by)
            alias_map = self._build_table_alias_map(tables)

            first_schema, first_table = self._sanitize_table_name(tables[0]["name"])
            first_alias = alias_map[f"{first_schema}.{first_table}"]

            select_parts = [
                f"{g['sql_expression']} AS {g['output_alias']}" for g in normalized["group_by"]
            ] + [
                f"{m['sql_expression']} AS {m['metric_alias']}" for m in normalized["aggregations"]
            ]

            query = f"SELECT {', '.join(select_parts)} FROM {first_schema}.{first_table} AS {first_alias}"

            for join in joins:
                right_full = self._resolve_full_table_name(tables, join["right"])
                right_schema, right_table = self._sanitize_table_name(right_full)
                left_alias = self._resolve_alias(tables, join["left"])
                right_alias = self._resolve_alias(tables, join["right"])
                left_on = self._sanitize_identifier(join["left_on"], label="join left_on")
                right_on = self._sanitize_identifier(join["right_on"], label="join right_on")
                join_type = str(join.get("how", "inner") or "inner").strip().lower()
                if join_type not in self.VALID_JOIN_TYPES:
                    raise ValueError(f"Invalid join type: {join_type}")
                query += f" {join_type.upper()} JOIN {right_schema}.{right_table} AS {right_alias}"
                query += f" ON {left_alias}.{left_on} = {right_alias}.{right_on}"

            where_parts: list[str] = []
            for table in tables:
                schema, table_name = self._sanitize_table_name(table["name"])
                alias = alias_map[f"{schema}.{table_name}"]
                w = self._build_where_clauses(table.get("filters", []), alias)
                if w:
                    where_parts.append(w)
            if where_parts:
                query += f" WHERE {' AND '.join(where_parts)}"

            if normalized["group_by"]:
                exprs = [g["sql_expression"] for g in normalized["group_by"]]
                query += f" GROUP BY {', '.join(exprs)}"

            if normalized["having"]:
                having_clauses = [
                    self._build_sql_condition(
                        normalized["metric_sql_by_alias"][h["metric"]],
                        h["op"],
                        h["value"],
                    )
                    for h in normalized["having"]
                ]
                query += f" HAVING {' AND '.join(having_clauses)}"

            if normalized["order_by"]:
                order_parts = [f"{o['field']} {o['direction'].upper()}" for o in normalized["order_by"]]
                query += f" ORDER BY {', '.join(order_parts)}"

            if limit and limit > 0:
                query += f" LIMIT {int(limit)}"

            logger.debug("[DynamicQuery][Aggregate] SQL: %s", query)
            result = await self._session.execute(text(query))
            rows = result.fetchall()
            columns = list(result.keys())
            data = [{col: self._serialize_value(val) for col, val in zip(columns, row)} for row in rows]
            return {"success": True, "rows": len(data), "columns": columns, "data": json.dumps(data), "error": ""}
        except Exception as e:
            logger.error("Error in _execute_aggregate: %s", e, exc_info=True)
            return {"success": False, "rows": 0, "columns": [], "data": "[]", "error": str(e)}
