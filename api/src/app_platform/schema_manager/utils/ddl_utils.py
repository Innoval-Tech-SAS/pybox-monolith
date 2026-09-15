from app_platform.schema_manager.constants.ddl_constants import NUMERIC_DEFAULT_RE, SAFE_DEFAULT_KEYWORDS
from app_platform.schema_manager.constants.query_constants import IDENTIFIER_RE
from app_platform.schema_manager.schemas.database_schemas import ColumnDataType, ColumnDefinition
from app_platform.schema_manager.utils.query_utils import sql_literal


def validate_ident(name: str, label: str) -> str:
    if not IDENTIFIER_RE.match(name):
        raise ValueError(f"Identificador inválido para {label}: '{name}'")
    return name


def render_default_value(raw: str) -> str:
    """Renderiza un DEFAULT de DDL de forma segura: solo se permiten palabras
    clave/funciones conocidas y literales numéricos sin escapar; cualquier
    otro valor se trata como literal de texto y se escapa vía sql_literal.
    """
    value = raw.strip()
    upper = value.upper()
    if upper in SAFE_DEFAULT_KEYWORDS:
        return upper
    if NUMERIC_DEFAULT_RE.match(value):
        return value
    return sql_literal(value)


def build_column_type(col: ColumnDefinition) -> str:
    if col.data_type == ColumnDataType.VARCHAR and col.length > 0:
        return f"VARCHAR({col.length})"
    if col.data_type == ColumnDataType.CHAR and col.length > 0:
        return f"CHAR({col.length})"
    if col.data_type == ColumnDataType.NUMERIC:
        if col.precision > 0 and col.scale > 0:
            return f"NUMERIC({col.precision},{col.scale})"
        if col.precision > 0:
            return f"NUMERIC({col.precision})"
    return col.data_type.value


def build_column_ddl(col: ColumnDefinition) -> str:
    name = validate_ident(col.name, "column name")
    col_type = build_column_type(col)
    parts = [f'"{name}" {col_type}']
    if col.primary_key:
        parts.append("PRIMARY KEY")
    else:
        if not col.nullable:
            parts.append("NOT NULL")
        if col.unique:
            parts.append("UNIQUE")
    if col.default_value:
        parts.append(f"DEFAULT {render_default_value(col.default_value)}")
    return " ".join(parts)
