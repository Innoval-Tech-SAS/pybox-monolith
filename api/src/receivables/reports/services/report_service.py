import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Sequence

import polars as pl
from fastapi import HTTPException, status

from core.config.logger import logger
from core.config.paths import UPLOADS_ROOT
from app_platform.schema_manager.services.dml_service import DmlService
from receivables.reports.models.report_execution_model import ReportExecutionModel
from receivables.reports.models.report_model import ReportModel
from receivables.reports.repository.report_execution_repository import ReportExecutionRepository
from receivables.reports.repository.report_repository import ReportRepository
from receivables.reports.schemas.report_schemas import ReportCreateRequest, ReportExecuteRequest, ReportUpdateRequest


class ReportService:

    def __init__(
        self,
        report_repo: ReportRepository,
        execution_repo: ReportExecutionRepository,
        dml_service: DmlService,
    ) -> None:
        self._report_repo = report_repo
        self._execution_repo = execution_repo
        self._dml = dml_service

    async def create(self, organization_id: uuid.UUID, data: ReportCreateRequest) -> ReportModel:
        report = ReportModel(
            name=data.name,
            description=data.description,
            report_config=data.report_config.model_dump(by_alias=False),
            organization_id=organization_id,
        )
        return await self._report_repo.add(report)

    async def list_by_org(self, organization_id: uuid.UUID) -> Sequence[ReportModel]:
        return await self._report_repo.get_by_organization_id(organization_id)

    async def get(self, report_id: uuid.UUID, organization_id: uuid.UUID) -> ReportModel:
        report = await self._report_repo.get_by_id(report_id)
        if not report or report.organization_id != organization_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Reporte no encontrado")
        return report

    async def update(self, report_id: uuid.UUID, organization_id: uuid.UUID, data: ReportUpdateRequest) -> ReportModel:
        report = await self.get(report_id, organization_id)
        if data.name is not None:
            report.name = data.name
        if data.description is not None:
            report.description = data.description
        if data.report_config is not None:
            report.report_config = data.report_config.model_dump(by_alias=False)
        return await self._report_repo.update(report)

    async def delete(self, report_id: uuid.UUID, organization_id: uuid.UUID) -> None:
        report = await self.get(report_id, organization_id)
        await self._report_repo.delete(report)

    async def execute(
        self,
        report_id: uuid.UUID,
        organization_id: uuid.UUID,
        request: ReportExecuteRequest,
        user_id: uuid.UUID,
    ) -> dict[str, Any]:
        report = await self.get(report_id, organization_id)
        config = report.report_config

        result = await self._dml.execute_query(
            tables=config.get("tables", []),
            joins=config.get("joins", []),
            limit=request.limit,
            query_mode=config.get("query_mode", "detail"),
            group_by=config.get("group_by", []),
            aggregations=config.get("aggregations", []),
            having=config.get("having", []),
            order_by=config.get("order_by", []),
        )

        if not result["success"]:
            logger.error("[ReportService] Error ejecutando reporte %s: %s", report_id, result["error"])
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, result["error"])

        df = self._to_dataframe(result)
        file_name: str | None = None
        file_path: str | None = None

        if request.mode == "audit":
            file_name, file_path = self._save_audit_file(
                organization_id=organization_id,
                report_id=report_id,
                report_name=report.name,
                df=df,
            )
            execution = ReportExecutionModel(
                report_id=report_id,
                mode=request.mode,
                file_name=file_name,
                file_path=file_path,
                rows=len(df),
                columns=df.columns,
                executed_by=user_id,
            )
            await self._execution_repo.add(execution)

        return {
            "success": True,
            "rows": len(df),
            "columns": df.columns,
            "data": df.to_dicts(),
            "mode": request.mode,
            "file_name": file_name,
            "file_path": file_path,
        }

    async def list_executions(self, report_id: uuid.UUID, organization_id: uuid.UUID) -> Sequence[ReportExecutionModel]:
        await self.get(report_id, organization_id)
        return await self._execution_repo.get_by_report(report_id)

    def _to_dataframe(self, result: dict[str, Any]) -> pl.DataFrame:
        import json
        data = json.loads(result["data"])
        if not data:
            return pl.DataFrame(schema={col: pl.Utf8 for col in result["columns"]})
        return pl.DataFrame(data)

    def _save_audit_file(
        self,
        organization_id: uuid.UUID,
        report_id: uuid.UUID,
        report_name: str,
        df: pl.DataFrame,
    ) -> tuple[str, str]:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", report_name)
        file_name = f"{timestamp}_{safe_name}.csv"

        dir_path = os.path.join(UPLOADS_ROOT, "organizations", str(organization_id), "reports", str(report_id))
        os.makedirs(dir_path, exist_ok=True)

        abs_path = os.path.join(dir_path, file_name)
        df.write_csv(abs_path)

        rel_path = os.path.relpath(abs_path, UPLOADS_ROOT)
        return file_name, rel_path
