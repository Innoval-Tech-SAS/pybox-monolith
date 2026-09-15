"""Tests directos de `ReportRepository`/`ReportExecutionRepository`: paginación,
soft-delete, y el OR de `get_global_and_by_organization` (reportes globales +
reportes propios de la organización, ambos solo si `is_active`)."""

import uuid
from datetime import datetime, timedelta, timezone

from receivables.reports.models.report_execution_model import ReportExecutionModel
from receivables.reports.models.report_model import ReportModel
from receivables.reports.repository.report_execution_repository import ReportExecutionRepository
from receivables.reports.repository.report_repository import ReportRepository
from tests.receivables.conftest import build_organization


class TestGetByOrganizationId:
    async def test_total_excludes_soft_deleted_and_other_orgs(self, db_session):
        org = build_organization()
        other_org = build_organization()
        db_session.add_all([org, other_org])
        await db_session.flush()

        db_session.add_all([
            ReportModel(name="A", report_config={"tables": []}, organization_id=org.id),
            ReportModel(name="B", report_config={"tables": []}, organization_id=org.id),
            ReportModel(
                name="Borrado", report_config={"tables": []}, organization_id=org.id,
                deleted_at=datetime.now(timezone.utc),
            ),
            ReportModel(name="Otra org", report_config={"tables": []}, organization_id=other_org.id),
        ])
        await db_session.flush()

        repo = ReportRepository(db_session)
        items, total = await repo.get_by_organization_id(org.id, page=1, page_size=10)

        assert total == 2
        assert len(items) == 2

    async def test_pagination_second_page(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        for i in range(3):
            db_session.add(ReportModel(name=f"R{i}", report_config={"tables": []}, organization_id=org.id))
        await db_session.flush()

        repo = ReportRepository(db_session)
        items, total = await repo.get_by_organization_id(org.id, page=2, page_size=2)

        assert total == 3
        assert len(items) == 1


class TestGetGlobalAndByOrganization:
    async def test_includes_global_and_own_org_reports_only_if_active(self, db_session):
        org = build_organization()
        other_org = build_organization()
        db_session.add_all([org, other_org])
        await db_session.flush()

        own_active = ReportModel(name="Propio", report_config={"tables": []}, organization_id=org.id, is_active=True)
        own_inactive = ReportModel(
            name="Propio inactivo", report_config={"tables": []}, organization_id=org.id, is_active=False
        )
        global_active = ReportModel(
            name="Global", report_config={"tables": []}, organization_id=other_org.id, is_active=True, is_global=True
        )
        global_inactive = ReportModel(
            name="Global inactivo", report_config={"tables": []}, organization_id=other_org.id,
            is_active=False, is_global=True,
        )
        other_org_report = ReportModel(
            name="Otra org, no global", report_config={"tables": []}, organization_id=other_org.id, is_active=True
        )
        db_session.add_all([own_active, own_inactive, global_active, global_inactive, other_org_report])
        await db_session.flush()

        repo = ReportRepository(db_session)
        result = await repo.get_global_and_by_organization(org.id)

        assert {r.id for r in result} == {own_active.id, global_active.id}


class TestReportExecutionRepository:
    async def test_get_by_report_orders_most_recent_first(self, db_session, real_admin_user_id):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        report = ReportModel(name="R", report_config={"tables": []}, organization_id=org.id)
        db_session.add(report)
        await db_session.flush()

        now = datetime.now(timezone.utc)
        older = ReportExecutionModel(
            report_id=report.id, mode="preview", rows=1, columns=["a"], executed_by=real_admin_user_id,
            created_at=now - timedelta(days=1),
        )
        db_session.add(older)
        await db_session.flush()
        newer = ReportExecutionModel(
            report_id=report.id, mode="audit", rows=2, columns=["a"], executed_by=real_admin_user_id,
            created_at=now,
        )
        db_session.add(newer)
        await db_session.flush()

        repo = ReportExecutionRepository(db_session)
        result = await repo.get_by_report(report.id)

        assert [e.id for e in result] == [newer.id, older.id]
