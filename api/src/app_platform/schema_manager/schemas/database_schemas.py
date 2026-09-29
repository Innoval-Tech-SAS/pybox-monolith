from enum import Enum
from typing import Any

from pydantic import Field

from core.base.schema_base import BaseSchema


class ColumnDataType(str, Enum):
    TEXT = "TEXT"
    VARCHAR = "VARCHAR"
    CHAR = "CHAR"
    INTEGER = "INTEGER"
    BIGINT = "BIGINT"
    SMALLINT = "SMALLINT"
    NUMERIC = "NUMERIC"
    FLOAT = "FLOAT"
    DOUBLE = "DOUBLE PRECISION"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    TIMESTAMP = "TIMESTAMP"
    TIMESTAMPTZ = "TIMESTAMPTZ"
    UUID = "UUID"
    JSONB = "JSONB"
    JSON = "JSON"


class AlterAction(str, Enum):
    ADD_COLUMN = "ADD_COLUMN"
    DROP_COLUMN = "DROP_COLUMN"
    MODIFY_COLUMN = "MODIFY_COLUMN"
    RENAME_COLUMN = "RENAME_COLUMN"


class ColumnDefinition(BaseSchema):
    name: str = Field(description="Nombre de la columna")
    data_type: ColumnDataType = Field(
        default=ColumnDataType.TEXT, description="Tipo de dato SQL de la columna"
    )
    nullable: bool = Field(
        default=True, description="Indica si la columna acepta valores nulos"
    )
    default_value: str | None = Field(
        default=None, description="Valor por defecto de la columna"
    )
    length: int = Field(
        default=0, description="Longitud máxima (para VARCHAR/CHAR), 0 si no aplica"
    )
    precision: int = Field(
        default=0, description="Precisión numérica (para NUMERIC), 0 si no aplica"
    )
    scale: int = Field(
        default=0,
        description="Escala numérica (decimales, para NUMERIC), 0 si no aplica",
    )
    primary_key: bool = Field(
        default=False, description="Indica si la columna es llave primaria"
    )
    unique: bool = Field(
        default=False, description="Indica si la columna tiene restricción de unicidad"
    )


class TableFilter(BaseSchema):
    column: str = Field(description="Nombre de la columna a filtrar")
    op: str = Field(
        default="=", description="Operador de comparación (=, !=, >, <, LIKE, IN, etc.)"
    )
    value: Any = Field(
        default=None, description="Valor contra el que se compara la columna"
    )


class JoinCondition(BaseSchema):
    left: str = Field(description="Nombre o alias de la tabla izquierda")
    right: str = Field(description="Nombre o alias de la tabla derecha")
    left_on: str = Field(description="Columna de la tabla izquierda usada en el join")
    right_on: str = Field(description="Columna de la tabla derecha usada en el join")
    how: str = Field(
        default="inner", description="Tipo de join: inner, left, right o outer"
    )


class GroupByField(BaseSchema):
    table: str | None = Field(
        default=None, description="Nombre o alias de la tabla del campo, si aplica"
    )
    column: str = Field(description="Columna por la que se agrupa")
    alias: str | None = Field(
        default=None, description="Alias del campo agrupado en el resultado"
    )


class AggregationSpec(BaseSchema):
    function: str = Field(
        description="Función de agregación a aplicar (SUM, COUNT, AVG, MIN, MAX, etc.)"
    )
    table: str | None = Field(
        default=None, description="Nombre o alias de la tabla de la columna agregada"
    )
    column: str = Field(description="Columna sobre la que se aplica la agregación")
    alias: str | None = Field(
        default=None, description="Alias del resultado de la agregación"
    )


class HavingCondition(BaseSchema):
    metric: str = Field(
        description="Alias de la métrica agregada sobre la que se filtra"
    )
    op: str = Field(description="Operador de comparación (=, !=, >, <, etc.)")
    value: Any = Field(
        default=None, description="Valor contra el que se compara la métrica"
    )


class OrderBySpec(BaseSchema):
    field: str = Field(description="Campo o alias por el que se ordena")
    direction: str = Field(default="asc", description="Dirección del orden: asc o desc")


class TableQuery(BaseSchema):
    name: str = Field(description="Nombre de la tabla")
    alias: str | None = Field(
        default=None, description="Alias de la tabla en la consulta"
    )
    columns: list[str] = Field(
        default_factory=list, description="Columnas a seleccionar de la tabla"
    )
    filters: list[TableFilter] = Field(
        default_factory=list, description="Filtros aplicados a la tabla"
    )


class DynamicQueryRequest(BaseSchema):
    tables: list[TableQuery] = Field(
        description="Tablas consultadas y sus columnas/filtros"
    )
    joins: list[JoinCondition] = Field(
        default_factory=list, description="Condiciones de join entre tablas"
    )
    limit: int = Field(default=1000, description="Máximo de filas a retornar")
    query_mode: str = Field(
        default="detail", description="Modo de consulta: detail o aggregate"
    )
    group_by: list[GroupByField] = Field(
        default_factory=list, description="Campos de agrupación"
    )
    aggregations: list[AggregationSpec] = Field(
        default_factory=list, description="Funciones de agregación a calcular"
    )
    having: list[HavingCondition] = Field(
        default_factory=list,
        description="Condiciones aplicadas sobre los resultados agregados",
    )
    order_by: list[OrderBySpec] = Field(
        default_factory=list, description="Orden de los resultados"
    )


class DynamicQueryResponse(BaseSchema):
    success: bool = Field(description="Indica si la consulta se ejecutó correctamente")
    rows: int = Field(description="Cantidad de filas retornadas")
    columns: list[str] = Field(description="Nombres de las columnas resultantes")
    data: str = Field(description="Datos resultantes serializados")
    error: str = Field(default="", description="Mensaje de error si la consulta falló")


class FieldInfo(BaseSchema):
    name: str = Field(description="Nombre de la columna")
    type: str = Field(description="Tipo de dato de la columna en la base de datos")
    enum_values: list[str] | None = Field(
        default=None,
        description=(
            "Valores permitidos, en orden de declaración, si la columna es un "
            "enum de PostgreSQL; null en cualquier otro caso"
        ),
    )


class CreateDatabaseRequest(BaseSchema):
    database_name: str = Field(description="Nombre de la base de datos a crear")


class CreateTableRequest(BaseSchema):
    table_name: str = Field(description="Nombre de la tabla a crear")
    columns: list[ColumnDefinition] = Field(
        description="Definición de las columnas de la tabla"
    )


class AlterTableRequest(BaseSchema):
    action: AlterAction = Field(
        description=(
            "Acción a realizar: ADD_COLUMN, DROP_COLUMN, MODIFY_COLUMN o RENAME_COLUMN"
        )
    )
    column: ColumnDefinition | None = Field(
        default=None,
        description="Definición de la columna (para ADD_COLUMN o MODIFY_COLUMN)",
    )
    column_name: str | None = Field(
        default=None,
        description="Nombre de la columna afectada (para DROP_COLUMN o RENAME_COLUMN)",
    )
    new_column_name: str | None = Field(
        default=None, description="Nuevo nombre de la columna (para RENAME_COLUMN)"
    )


class OperationResponse(BaseSchema):
    success: bool = Field(
        description="Indica si la operación se completó correctamente"
    )
    message: str = Field(
        description="Mensaje descriptivo del resultado de la operación"
    )
