import re

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

VALID_WHERE_OPERATORS: set[str] = {
    "=", "!=", "<>", ">", "<", ">=", "<=",
    "in", "not_in", "like", "ilike", "between", "is_null", "is_not_null",
}
VALID_HAVING_OPERATORS: set[str] = {
    "=", "!=", "<>", ">", "<", ">=", "<=", "in", "not_in", "between",
}
JOIN_SQL_KEYWORDS: dict[str, str] = {
    "inner": "INNER JOIN",
    "left": "LEFT JOIN",
    "right": "RIGHT JOIN",
    "full": "FULL JOIN",
}
VALID_JOIN_TYPES: set[str] = set(JOIN_SQL_KEYWORDS)
VALID_AGG_FUNCTIONS: set[str] = {"count", "sum", "avg", "min", "max"}

# Tablas que segments/reports pueden consultar vía DmlService, y cómo acotar cada
# una a los portafolios/organizaciones permitidos del caller. Ninguna de estas
# tablas tiene organization_id propio salvo metodos_pago y contactos: el resto se
# ancla a creditos (que sí tiene id_portafolio) por la FK más cercana. Cualquier
# tabla que no esté aquí queda fuera del alcance de reportes/segmentos.
TENANT_SCOPED_TABLES: dict[str, str] = {
    "public.deudores": (
        "EXISTS (SELECT 1 FROM public.creditos __sc WHERE __sc.id_deudor = {alias}.id "
        "AND __sc.id_portafolio IN ({portfolio_ids}) AND __sc.eliminado_en IS NULL)"
    ),
    "public.metodos_contacto": (
        "EXISTS (SELECT 1 FROM public.creditos __sc WHERE __sc.id_deudor = {alias}.id_deudor "
        "AND __sc.id_portafolio IN ({portfolio_ids}) AND __sc.eliminado_en IS NULL)"
    ),
    "public.direcciones": (
        "EXISTS (SELECT 1 FROM public.creditos __sc WHERE __sc.id_deudor = {alias}.id_deudor "
        "AND __sc.id_portafolio IN ({portfolio_ids}) AND __sc.eliminado_en IS NULL)"
    ),
    "public.creditos": "{alias}.id_portafolio IN ({portfolio_ids})",
    "public.pagos": (
        "EXISTS (SELECT 1 FROM public.creditos __sc WHERE __sc.id = {alias}.id_credito "
        "AND __sc.id_portafolio IN ({portfolio_ids}) AND __sc.eliminado_en IS NULL)"
    ),
    "public.metodos_pago": "{alias}.id_organizacion IN ({organization_ids})",
    "public.contactos": (
        "({alias}.id_portafolio IN ({portfolio_ids}) OR {alias}.id_organizacion IN ({organization_ids}))"
    ),
}

# Columnas que se guardan cifradas (AES-GCM con nonce aleatorio, así que nunca coinciden
# por igualdad) y que solo se pueden buscar por su columna hash hermana (HMAC-SHA256,
# ver EncryptService.hash_document). El filtro se reescribe a la columna hash y el valor
# se hashea en el servidor; el operador solo puede ser de igualdad/lista/nulo.
HASHED_FILTER_COLUMNS: dict[str, dict[str, str]] = {
    "public.deudores": {"numero_documento": "numero_documento_hash"},
}
HASHED_FILTER_OPERATORS: set[str] = {"=", "!=", "<>", "in", "not_in", "is_null", "is_not_null"}

# Columnas que se guardan cifradas y que `execute_query(decrypt_sensitive=True)` devuelve
# en claro. Es una decisión del caller (según el permiso del usuario sobre el dato): por
# defecto salen tal cual están en la base (token `v1:...`).
ENCRYPTED_COLUMNS: dict[str, set[str]] = {
    "public.deudores": {"numero_documento"},
}

# Código HTTP con el que se reporta un fallo de la consulta: 422 cuando el usuario puede
# corregirlo editando el segmento/reporte, 500 cuando es un fallo del servidor.
INVALID_QUERY_STATUS_CODE = 422
QUERY_FAILURE_STATUS_CODE = 500

# SQLSTATE de Postgres -> qué le pasó a la consulta, en términos del usuario. Solo los
# errores que se arreglan cambiando la configuración de la consulta (422); cualquier otro
# SQLSTATE se reporta como fallo del servidor con su código. Al final se anexa el mensaje
# del servidor (nunca el SQL), que nombra la columna/operador/valor exacto.
DB_ERROR_MESSAGES: dict[str, str] = {
    "42703": "Una de las columnas configuradas no existe en su tabla.",
    "42P01": "Una de las tablas configuradas no existe.",
    "42702": "Una columna es ambigua: hay que indicar a qué tabla pertenece.",
    "42803": "Toda columna que no sea una agregación debe estar en la agrupación (GROUP BY).",
    "42883": "El operador del filtro no es compatible con el tipo de dato de la columna.",
    "42804": "El tipo del valor no coincide con el tipo de la columna.",
    "22P02": "El valor del filtro no tiene un formato válido para el tipo de la columna.",
    "22007": "Uno de los filtros tiene una fecha u hora con formato inválido.",
    "22008": "Uno de los filtros tiene una fecha u hora fuera de rango.",
    "22003": "Un valor numérico está fuera del rango permitido.",
    "22012": "La consulta produjo una división por cero.",
    "57014": "La consulta tardó demasiado y fue cancelada; agrega filtros o reduce el límite de filas.",
}

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
