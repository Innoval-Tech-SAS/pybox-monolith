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


class ReportQueryConfig(BaseSchema):
    tables: list[TableQuery] = Field(description="Tablas consultadas y sus columnas/filtros")
    joins: list[JoinCondition] = Field(default_factory=list, description="Condiciones de join entre tablas")
    query_mode: str = Field(default="detail", description="Modo de consulta: detail o aggregate")
    group_by: list[GroupByField] = Field(default_factory=list, description="Campos de agrupación")
    aggregations: list[AggregationSpec] = Field(default_factory=list, description="Funciones de agregación a calcular")
    having: list[HavingCondition] = Field(default_factory=list, description="Condiciones aplicadas sobre los resultados agregados")
    order_by: list[OrderBySpec] = Field(default_factory=list, description="Orden de los resultados")


class ReportCreateRequest(BaseSchema):
    name: str = Field(description="Nombre del reporte")
    description: str | None = Field(default=None, description="Descripción del reporte")
    report_config: ReportQueryConfig = Field(description="Configuración de la consulta del reporte")


class ReportUpdateRequest(BaseSchema):
    name: str | None = Field(default=None, description="Nuevo nombre")
    description: str | None = Field(default=None, description="Nueva descripción")
    report_config: ReportQueryConfig | None = Field(default=None, description="Nueva configuración de la consulta")


class ReportExecuteRequest(BaseSchema):
    mode: Literal["preview", "audit"] = Field(default="preview", description="Modo de ejecución: preview (limitado) o audit (completo, se persiste)")
    limit: int | None = Field(default=None, ge=1, description="Límite de filas a retornar en modo preview")


class ReportResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID del reporte")
    name: str = Field(description="Nombre del reporte")
    description: str | None = Field(description="Descripción del reporte")
    report_config: dict[str, Any] = Field(description="Configuración de la consulta del reporte")
    organization_id: uuid.UUID = Field(description="ID de la organización")
    created_at: datetime = Field(description="Fecha de creación")


class ReportExecuteResponse(BaseSchema):
    success: bool = Field(description="Indica si la ejecución fue exitosa")
    rows: int = Field(description="Cantidad de filas retornadas")
    columns: list[str] = Field(description="Nombres de las columnas resultantes")
    data: list[dict[str, Any]] = Field(description="Datos resultantes de la consulta")
    mode: str = Field(description="Modo en que se ejecutó: preview o audit")
    file_name: str | None = Field(default=None, description="Nombre del archivo exportado (modo audit)")
    file_path: str | None = Field(default=None, description="Ruta del archivo exportado (modo audit)")


class ReportExecutionResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID de la ejecución")
    report_id: uuid.UUID = Field(description="ID del reporte ejecutado")
    mode: str = Field(description="Modo de ejecución: preview o audit")
    file_name: str | None = Field(description="Nombre del archivo exportado")
    file_path: str | None = Field(description="Ruta del archivo exportado")
    rows: int = Field(description="Cantidad de filas obtenidas")
    columns: list[str] = Field(description="Nombres de las columnas resultantes")
    executed_by: uuid.UUID = Field(description="ID del usuario que ejecutó el reporte")
    created_at: datetime = Field(description="Fecha de ejecución")
