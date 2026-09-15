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
