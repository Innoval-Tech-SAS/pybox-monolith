from typing import Any
from enum import Enum

from pydantic import Field

from base.schema_base import BaseSchema


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
    name: str
    data_type: ColumnDataType = ColumnDataType.TEXT
    nullable: bool = True
    default_value: str | None = None
    length: int = 0
    precision: int = 0
    scale: int = 0
    primary_key: bool = False
    unique: bool = False


class TableFilter(BaseSchema):
    column: str
    op: str = "="
    value: Any = None


class JoinCondition(BaseSchema):
    left: str
    right: str
    left_on: str
    right_on: str
    how: str = "inner"


class GroupByField(BaseSchema):
    table: str | None = None
    column: str
    alias: str | None = None


class AggregationSpec(BaseSchema):
    function: str
    table: str | None = None
    column: str
    alias: str | None = None


class HavingCondition(BaseSchema):
    metric: str
    op: str
    value: Any = None


class OrderBySpec(BaseSchema):
    field: str
    direction: str = "asc"


class TableQuery(BaseSchema):
    name: str
    alias: str | None = None
    columns: list[str] = Field(default_factory=list)
    filters: list[TableFilter] = Field(default_factory=list)


class DynamicQueryRequest(BaseSchema):
    organization_id: str
    tables: list[TableQuery]
    joins: list[JoinCondition] = Field(default_factory=list)
    limit: int = 1000
    query_mode: str = "detail"
    group_by: list[GroupByField] = Field(default_factory=list)
    aggregations: list[AggregationSpec] = Field(default_factory=list)
    having: list[HavingCondition] = Field(default_factory=list)
    order_by: list[OrderBySpec] = Field(default_factory=list)


class DynamicQueryResponse(BaseSchema):
    success: bool
    rows: int
    columns: list[str]
    data: str
    error: str = ""


class FieldInfo(BaseSchema):
    name: str
    type: str


class CreateDatabaseRequest(BaseSchema):
    database_name: str


class CreateTableRequest(BaseSchema):
    table_name: str
    columns: list[ColumnDefinition]


class AlterTableRequest(BaseSchema):
    action: AlterAction
    column: ColumnDefinition | None = None
    column_name: str | None = None
    new_column_name: str | None = None


class OperationResponse(BaseSchema):
    success: bool
    message: str
