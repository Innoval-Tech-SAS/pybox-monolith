import re

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

OPERATOR_ALIASES: dict[str, str] = {
    "is_null": "is_null",
    "is_not_null": "is_not_null",
    "in": "in",
    "not_in": "not_in",
    "notin": "not_in",
    "like": "like",
    "ilike": "ilike",
    "between": "between",
    "eq": "=",
    "ne": "!=",
    "neq": "!=",
    "lt": "<",
    "lte": "<=",
    "gt": ">",
    "gte": ">=",
}
