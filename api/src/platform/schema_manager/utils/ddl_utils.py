from platform.schema_manager.constants.query_constants import IDENTIFIER_RE
from platform.schema_manager.schemas.database_schemas import ColumnDataType, ColumnDefinition


def validate_ident(name: str, label: str) -> str:
    if not IDENTIFIER_RE.match(name):
        raise ValueError(f"Identificador inválido para {label}: '{name}'")
    return name


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
        parts.append(f"DEFAULT {col.default_value}")
    return " ".join(parts)
