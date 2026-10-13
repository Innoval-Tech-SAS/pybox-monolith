"""Tests unitarios de `ReportService`: CRUD y las dos ramas de `execute` (preview vs
audit). `DmlService` se mockea (unittest.mock) por la misma razón que en
`test_segment_service.py`: la ejecución dinámica de queries es de
`app_platform.schema_manager`, no de este servicio. Los permisos por rol
(`require_admin_or_org`) están en el controller, no acá -- se cubren en
`test_report_controller.py`."""

import json
import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app_platform.schema_manager.services.dml_service import DmlService
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository
from receivables.reports.repository.report_execution_repository import (
    ReportExecutionRepository,
)
from receivables.reports.repository.report_repository import ReportRepository
from receivables.reports.schemas.report_schemas import (
    ReportCreateRequest,
    ReportExecuteRequest,
    ReportQueryConfig,
    ReportUpdateRequest,
)
from receivables.reports.services.report_service import ReportService
from tests.receivables.conftest import build_organization, build_portfolio


def build_service(db_session, dml_mock=None) -> ReportService:
    return ReportService(
        report_repo=ReportRepository(db_session),
        execution_repo=ReportExecutionRepository(db_session),
        dml_service=dml_mock or AsyncMock(spec=DmlService),
        portfolio_repo=PortfolioRepository(db_session),
    )


def query_config(**overrides) -> ReportQueryConfig:
    defaults = dict(tables=[{"name": "creditos", "columns": ["numero_credito"]}])
    defaults.update(overrides)
    return ReportQueryConfig.model_validate(defaults)


@pytest.fixture
async def org(db_session):
    org = build_organization()
    db_session.add(org)
    await db_session.flush()
    return org


class TestCrud:
    async def test_create_and_get(self, db_session, org):
        service = build_service(db_session)
        report = await service.create(
            org.id, ReportCreateRequest(name="Mora", report_config=query_config())
        )

        fetched = await service.get(report.id, org.id)
        assert fetched.id == report.id
        assert fetched.name == "Mora"

    async def test_get_wrong_org_raises_404(self, db_session, org):
        other_org = build_organization()
        db_session.add(other_org)
        await db_session.flush()
        service = build_service(db_session)
        report = await service.create(
            org.id, ReportCreateRequest(name="Mora", report_config=query_config())
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.get(report.id, other_org.id)
        assert exc_info.value.status_code == 404

    async def test_list_by_org_paginates(self, db_session, org):
        service = build_service(db_session)
        for i in range(3):
            await service.create(
                org.id, ReportCreateRequest(name=f"R{i}", report_config=query_config())
            )

        items, total = await service.list_by_org(org.id, page=1, page_size=2)
        assert total == 3
        assert len(items) == 2

    async def test_update_changes_fields(self, db_session, org):
        service = build_service(db_session)
        report = await service.create(
            org.id, ReportCreateRequest(name="Original", report_config=query_config())
        )

        updated = await service.update(
            report.id, org.id, ReportUpdateRequest(name="Renombrado")
        )
        assert updated.name == "Renombrado"

    async def test_delete_removes_report(self, db_session, org):
        service = build_service(db_session)
        report = await service.create(
            org.id, ReportCreateRequest(name="Borrar", report_config=query_config())
        )

        await service.delete(report.id, org.id)

        with pytest.raises(HTTPException) as exc_info:
            await service.get(report.id, org.id)
        assert exc_info.value.status_code == 404


class TestExecute:
    def _ok_result(self, rows: list[dict]) -> dict:
        columns = list(rows[0].keys()) if rows else []
        return {
            "success": True,
            "data": json.dumps(rows),
            "columns": columns,
            "rows": len(rows),
            "error": "",
        }

    async def test_preview_does_not_persist_execution(self, db_session, org):
        dml_mock = AsyncMock(spec=DmlService)
        dml_mock.execute_query.return_value = self._ok_result(
            [{"numero_credito": "CR-1"}]
        )
        service = build_service(db_session, dml_mock)
        report = await service.create(
            org.id, ReportCreateRequest(name="Preview", report_config=query_config())
        )

        result = await service.execute(
            report.id, org.id, ReportExecuteRequest(mode="preview"), uuid.uuid4()
        )

        assert result["rows"] == 1
        assert result["file_name"] is None
        executions = await service.list_executions(report.id, org.id)
        assert len(executions) == 0

    async def test_audit_persists_execution_and_file(
        self, db_session, org, real_admin_user_id
    ):
        dml_mock = AsyncMock(spec=DmlService)
        dml_mock.execute_query.return_value = self._ok_result(
            [{"numero_credito": "CR-1"}, {"numero_credito": "CR-2"}]
        )
        service = build_service(db_session, dml_mock)
        report = await service.create(
            org.id, ReportCreateRequest(name="Audit", report_config=query_config())
        )

        result = await service.execute(
            report.id, org.id, ReportExecuteRequest(mode="audit"), real_admin_user_id
        )

        assert result["rows"] == 2
        assert result["file_name"] is not None
        assert result["document_id"] is not None

        executions = await service.list_executions(report.id, org.id)
        assert len(executions) == 1
        assert executions[0].mode == "audit"
        assert executions[0].executed_by == real_admin_user_id

    async def test_dml_failure_raises_500(self, db_session, org):
        dml_mock = AsyncMock(spec=DmlService)
        dml_mock.execute_query.return_value = {"success": False, "error": "boom"}
        service = build_service(db_session, dml_mock)
        report = await service.create(
            org.id, ReportCreateRequest(name="Falla", report_config=query_config())
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.execute(
                report.id, org.id, ReportExecuteRequest(mode="preview"), uuid.uuid4()
            )
        assert exc_info.value.status_code == 500

    async def test_execute_scopes_to_org_portfolios(self, db_session, org):
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        dml_mock = AsyncMock(spec=DmlService)
        dml_mock.execute_query.return_value = self._ok_result([])
        service = build_service(db_session, dml_mock)
        report = await service.create(
            org.id, ReportCreateRequest(name="Scoped", report_config=query_config())
        )

        await service.execute(
            report.id,
            org.id,
            ReportExecuteRequest(mode="preview", limit=25),
            uuid.uuid4(),
        )

        _, kwargs = dml_mock.execute_query.call_args
        assert kwargs["portfolio_ids"] == [portfolio.id]
        assert kwargs["organization_ids"] == [org.id]
        assert kwargs["limit"] == 25
