import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from schema_manager.constants.query_constants import (
    IDENTIFIER_RE,
    OPERATOR_ALIASES,
    VALID_AGG_FUNCTIONS,
    VALID_HAVING_OPERATORS,
    VALID_WHERE_OPERATORS,
)


def serialize_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def parse_json_if_string(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return value
    return value


def sql_literal(value: Any) -> str:
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


def sanitize_identifier(value: str | None, *, label: str) -> str:
    identifier = str(value or "").strip()
    if not identifier:
        raise ValueError(f"{label} is required")
    if not IDENTIFIER_RE.match(identifier):
        raise ValueError(f"Invalid {label}: {value}")
    return identifier


def sanitize_table_name(full_name: str) -> tuple[str, str]:
    if "." not in str(full_name or ""):
        raise ValueError(f"Table name must include schema: {full_name}")
    schema, table = full_name.split(".", 1)
    return sanitize_identifier(schema, label="schema"), sanitize_identifier(table, label="table")


def normalize_operator(op: str) -> str:
    normalized = str(op or "=").strip().lower().replace(" ", "_")
    return OPERATOR_ALIASES.get(normalized, normalized)


def ensure_operator_allowed(op: str, *, in_having: bool = False) -> str:
    normalized = normalize_operator(op)
    allowed = VALID_HAVING_OPERATORS if in_having else VALID_WHERE_OPERATORS
    if normalized not in allowed:
        raise ValueError(f"Invalid operator '{op}'")
    return normalized


def normalize_sort_direction(direction: str) -> str:
    normalized = str(direction or "asc").strip().lower()
    if normalized not in {"asc", "desc"}:
        raise ValueError(f"Invalid sort direction: {direction}")
    return normalized


def normalize_aggregate_function(function_name: str | None) -> str:
    normalized = str(function_name or "").strip().lower()
    if normalized not in VALID_AGG_FUNCTIONS:
        raise ValueError(f"Unsupported aggregation function: {function_name}")
    return normalized


def build_sql_condition(expression: str, operator: str, value: Any) -> str:
    if operator == "is_null":
        return f"{expression} IS NULL"
    if operator == "is_not_null":
        return f"{expression} IS NOT NULL"
    if operator == "in":
        values = value if isinstance(value, list) else [value]
        if not values:
            raise ValueError("IN operator requires at least one value")
        return f"{expression} IN ({', '.join(sql_literal(v) for v in values)})"
    if operator == "not_in":
        values = value if isinstance(value, list) else [value]
        if not values:
            raise ValueError("NOT IN operator requires at least one value")
        return f"{expression} NOT IN ({', '.join(sql_literal(v) for v in values)})"
    if operator == "between":
        values = value if isinstance(value, list) else []
        if len(values) != 2:
            raise ValueError("BETWEEN operator requires exactly two values")
        return f"{expression} BETWEEN {sql_literal(values[0])} AND {sql_literal(values[1])}"
    if operator == "like":
        return f"{expression} LIKE {sql_literal(value)}"
    if operator == "ilike":
        return f"{expression} ILIKE {sql_literal(value)}"
    sql_op = "<>" if operator == "!=" else operator
    return f"{expression} {sql_op} {sql_literal(value)}"


def build_where_clauses(filters: list[dict[str, Any]], alias: str) -> str:
    if not filters:
        return ""
    clauses = []
    for f in filters:
        column = sanitize_identifier(f["column"], label="filter column")
        op = ensure_operator_allowed(f.get("op", "="), in_having=False)
        value = parse_json_if_string(f.get("value"))
        clauses.append(build_sql_condition(f"{alias}.{column}", op, value))
    return " AND ".join(clauses)


def build_table_alias_map(tables: list[dict[str, Any]]) -> dict[str, str]:
    alias_map: dict[str, str] = {}
    alias_set: set[str] = set()
    for table in tables:
        schema, table_name = sanitize_table_name(table["name"])
        full_name = f"{schema}.{table_name}"
        alias = table.get("alias") or table_name
        alias = sanitize_identifier(alias, label=f"alias for {full_name}")
        if alias in alias_set:
            raise ValueError(f"Duplicate table alias: {alias}")
        alias_set.add(alias)
        alias_map[full_name] = alias
    return alias_map


def resolve_alias(tables: list[dict[str, Any]], table_ref: str | None) -> str:
    alias_map = build_table_alias_map(tables)
    if not table_ref:
        if len(alias_map) == 1:
            return next(iter(alias_map.values()))
        raise ValueError("Table reference is required when multiple tables are used")
    ref = str(table_ref).strip()
    if ref in alias_map.values():
        return sanitize_identifier(ref, label="table alias")
    schema, table = sanitize_table_name(ref)
    full_name = f"{schema}.{table}"
    if full_name not in alias_map:
        raise ValueError(f"Unknown table reference: {table_ref}")
    return alias_map[full_name]


def resolve_full_table_name(tables: list[dict[str, Any]], table_ref: str | None) -> str:
    alias_map = build_table_alias_map(tables)
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
    schema, table = sanitize_table_name(ref)
    full_name = f"{schema}.{table}"
    if full_name not in alias_map:
        raise ValueError(f"Unknown table reference: {table_ref}")
    return full_name


def build_select_parts(table: dict[str, Any], alias: str, *, prefixed_alias: bool = False) -> list[str]:
    columns = table.get("columns") or []
    if not columns:
        return [f"{alias}.*"]
    parts = []
    for raw_col in columns:
        col = sanitize_identifier(raw_col, label="column")
        parts.append(f"{alias}.{col} AS {alias}_{col}" if prefixed_alias else f"{alias}.{col}")
    return parts


def default_group_alias(alias_value: str | None, column: str) -> str:
    if alias_value:
        return sanitize_identifier(alias_value, label="group alias")
    return sanitize_identifier(column, label="group column")


def default_aggregation_alias(function_name: str, column: str, table_alias: str) -> str:
    fn = normalize_aggregate_function(function_name)
    if column == "*":
        return f"{fn}_all"
    return f"{fn}_{sanitize_identifier(table_alias, label='table alias')}_{sanitize_identifier(column, label='aggregation column')}"


def normalize_aggregate_specs(
    tables: list[dict[str, Any]],
    group_by: list[dict[str, Any]],
    aggregations: list[dict[str, Any]],
    having: list[dict[str, Any]],
    order_by: list[dict[str, Any]],
) -> dict[str, Any]:
    alias_map = build_table_alias_map(tables)
    output_aliases: set[str] = set()
    group_aliases: set[str] = set()
    metric_aliases: set[str] = set()
    metric_sql_by_alias: dict[str, str] = {}

    normalized_group_by: list[dict[str, Any]] = []
    for group in group_by:
        table_alias = resolve_alias(tables, group.get("table"))
        column = sanitize_identifier(group.get("column"), label="group_by column")
        output_alias = default_group_alias(group.get("alias"), column)
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
        fn = normalize_aggregate_function(metric.get("function"))
        raw_col = str(metric.get("column") or "").strip()
        if not raw_col:
            raise ValueError("Aggregation column is required")

        if raw_col == "*":
            if fn != "count":
                raise ValueError("Only COUNT supports column='*'")
            table_alias = resolve_alias(tables, metric.get("table")) if metric.get("table") else default_single_alias
            sql_expression = "COUNT(*)"
        else:
            table_alias = resolve_alias(tables, metric.get("table"))
            col = sanitize_identifier(raw_col, label="aggregation column")
            sql_expression = f"{fn.upper()}({table_alias}.{col})"

        metric_alias = metric.get("alias") or default_aggregation_alias(fn, raw_col, table_alias or "all")
        metric_alias = sanitize_identifier(metric_alias, label="aggregation alias")
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
        metric_alias = sanitize_identifier(condition.get("metric"), label="having metric")
        if metric_alias not in metric_aliases:
            raise ValueError(f"Unknown metric alias in HAVING: {metric_alias}")
        op = ensure_operator_allowed(condition.get("op", "="), in_having=True)
        value = parse_json_if_string(condition.get("value"))
        normalized_having.append({"metric": metric_alias, "op": op, "value": value})

    sortable_fields = group_aliases | metric_aliases
    normalized_order_by: list[dict[str, Any]] = []
    for ordering in order_by:
        field = sanitize_identifier(ordering.get("field"), label="order_by field")
        if field not in sortable_fields:
            raise ValueError(f"order_by field '{field}' must reference a group_by or aggregation alias")
        direction = normalize_sort_direction(ordering.get("direction", "asc"))
        normalized_order_by.append({"field": field, "direction": direction})

    return {
        "group_by": normalized_group_by,
        "aggregations": normalized_aggregations,
        "having": normalized_having,
        "order_by": normalized_order_by,
        "metric_sql_by_alias": metric_sql_by_alias,
    }


def is_aggregate_mode(
    query_mode: str,
    group_by: list[dict[str, Any]],
    aggregations: list[dict[str, Any]],
    having: list[dict[str, Any]],
    order_by: list[dict[str, Any]],
) -> bool:
    if str(query_mode or "").strip().lower() == "aggregate":
        return True
    return bool(group_by or aggregations or having or order_by)
