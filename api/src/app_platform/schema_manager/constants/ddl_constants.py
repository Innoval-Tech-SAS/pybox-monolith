"""Constantes de validación para DDL dinámico (defaults seguros, regex numérica)."""

import re

SAFE_DEFAULT_KEYWORDS = {
    "NULL",
    "TRUE",
    "FALSE",
    "CURRENT_TIMESTAMP",
    "CURRENT_DATE",
    "CURRENT_TIME",
    "NOW()",
    "GEN_RANDOM_UUID()",
    "UUID_GENERATE_V4()",
}
NUMERIC_DEFAULT_RE = re.compile(r"^-?\d+(\.\d+)?$")
