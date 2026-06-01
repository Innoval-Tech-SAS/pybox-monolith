import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Sequence

import polars as pl
from fastapi import HTTPException, status

from config.logger import logger
from config.paths import UPLOADS_ROOT
from databases.services.dml_service import DmlService
from segments.models.segment_execution_model import SegmentExecutionModel
from segments.models.segment_model import SegmentModel
from segments.repository.segment_execution_repository import SegmentExecutionRepository
from segments.repository.segment_repository import SegmentRepository
from segments.schemas.segment_schemas import SegmentCreateRequest, SegmentExecuteRequest, SegmentUpdateRequest


class SegmentService:

    def __init__(
        self,
        segment_repo: SegmentRepository,
        execution_repo: SegmentExecutionRepository,
        dml_service: DmlService,
    ) -> None:
        self._segment_repo = segment_repo
        self._execution_repo = execution_repo
        self._dml = dml_service

    async def create(self, organization_id: uuid.UUID, data: SegmentCreateRequest) -> SegmentModel:
        segment = SegmentModel(
            name=data.name,
            description=data.description,
            filter_criteria=data.filter_criteria.model_dump(by_alias=False),
            organization_id=organization_id,
        )
        return await self._segment_repo.add(segment)

    async def list_by_org(self, organization_id: uuid.UUID) -> Sequence[SegmentModel]:
        return await self._segment_repo.get_by_organization(organization_id)

    async def get(self, segment_id: int, organization_id: uuid.UUID) -> SegmentModel:
        segment = await self._segment_repo.get_by_id(segment_id)
        if not segment or segment.organization_id != organization_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Segmento no encontrado")
        return segment

    async def update(self, segment_id: int, organization_id: uuid.UUID, data: SegmentUpdateRequest) -> SegmentModel:
        segment = await self.get(segment_id, organization_id)
        if data.name is not None:
            segment.name = data.name
        if data.description is not None:
            segment.description = data.description
        if data.filter_criteria is not None:
            segment.filter_criteria = data.filter_criteria.model_dump(by_alias=False)
        return await self._segment_repo.update(segment)

    async def delete(self, segment_id: int, organization_id: uuid.UUID) -> None:
        segment = await self.get(segment_id, organization_id)
        await self._segment_repo.delete(segment)

    async def execute(
        self,
        segment_id: int,
        organization_id: uuid.UUID,
        request: SegmentExecuteRequest,
        user_id: int,
    ) -> dict[str, Any]:
        segment = await self.get(segment_id, organization_id)
        criteria = segment.filter_criteria

        result = await self._dml.execute_query(
            tables=criteria.get("tables", []),
            joins=criteria.get("joins", []),
            limit=request.limit,
            query_mode=criteria.get("query_mode", "detail"),
            group_by=criteria.get("group_by", []),
            aggregations=criteria.get("aggregations", []),
            having=criteria.get("having", []),
            order_by=criteria.get("order_by", []),
        )

        if not result["success"]:
            logger.error("[SegmentService] Error ejecutando segmento %d: %s", segment_id, result["error"])
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, result["error"])

        df = self._to_dataframe(result)
        file_name: str | None = None
        file_path: str | None = None

        if request.mode == "audit":
            file_name, file_path = self._save_audit_file(
                organization_id=organization_id,
                segment_id=segment_id,
                segment_name=segment.name,
                df=df,
            )
            execution = SegmentExecutionModel(
                segment_id=segment_id,
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

    async def list_executions(self, segment_id: int, organization_id: uuid.UUID) -> Sequence[SegmentExecutionModel]:
        await self.get(segment_id, organization_id)
        return await self._execution_repo.get_by_segment(segment_id)

    def _to_dataframe(self, result: dict[str, Any]) -> pl.DataFrame:
        import json
        data = json.loads(result["data"])
        if not data:
            return pl.DataFrame(schema={col: pl.Utf8 for col in result["columns"]})
        return pl.DataFrame(data)

    def _save_audit_file(
        self,
        organization_id: uuid.UUID,
        segment_id: int,
        segment_name: str,
        df: pl.DataFrame,
    ) -> tuple[str, str]:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", segment_name)
        file_name = f"{timestamp}_{safe_name}.csv"

        dir_path = os.path.join(UPLOADS_ROOT, "organizations", str(organization_id), "segments", str(segment_id))
        os.makedirs(dir_path, exist_ok=True)

        abs_path = os.path.join(dir_path, file_name)
        df.write_csv(abs_path)

        rel_path = os.path.relpath(abs_path, UPLOADS_ROOT)
        return file_name, rel_path
