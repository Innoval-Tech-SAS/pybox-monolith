import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from core.base.schema_base import BaseSchema
from app_platform.schema_manager.schemas.database_schemas import (
    AggregationSpec,
    GroupByField,
    HavingCondition,
    JoinCondition,
    OrderBySpec,
    TableQuery,
)


class SegmentQueryConfig(BaseSchema):
    tables: list[TableQuery]
    joins: list[JoinCondition] = Field(default_factory=list)
    query_mode: str = "detail"
    group_by: list[GroupByField] = Field(default_factory=list)
    aggregations: list[AggregationSpec] = Field(default_factory=list)
    having: list[HavingCondition] = Field(default_factory=list)
    order_by: list[OrderBySpec] = Field(default_factory=list)


class SegmentCreateRequest(BaseSchema):
    name: str
    description: str | None = None
    filter_criteria: SegmentQueryConfig


class SegmentUpdateRequest(BaseSchema):
    name: str | None = None
    description: str | None = None
    filter_criteria: SegmentQueryConfig | None = None


class SegmentExecuteRequest(BaseSchema):
    mode: Literal["preview", "audit"] = "preview"
    limit: int | None = Field(default=None, ge=1)


class SegmentResponse(BaseSchema):
    id: uuid.UUID
    name: str
    description: str | None
    filter_criteria: dict[str, Any]
    organization_id: uuid.UUID
    created_at: datetime


class SegmentExecuteResponse(BaseSchema):
    success: bool
    rows: int
    columns: list[str]
    data: list[dict[str, Any]]
    mode: str
    file_name: str | None = None
    file_path: str | None = None


class SegmentExecutionResponse(BaseSchema):
    id: uuid.UUID
    segment_id: uuid.UUID
    mode: str
    file_name: str | None
    file_path: str | None
    rows: int
    columns: list[str]
    executed_by: uuid.UUID
    created_at: datetime
