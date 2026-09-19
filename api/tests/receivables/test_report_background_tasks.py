"""Tests de `execute_and_notify` (reports/background_tasks.py): las 3 ramas del
try/except -- éxito, `HTTPException` (mora esperada, p. ej. reporte sin filas válidas)
y excepción genérica -- deben terminar en una notificación distinta para el usuario.

`ReportService.execute` se mockea (unittest.mock) para no depender de una
`DmlService` real: lo que se prueba acá es que el background task abre su propia
sesión y arma la notificación correcta según cómo termine `execute`, no la ejecución
de la query dinámica en sí (eso ya lo cubre `test_report_service.py` con mocks
propios, y `app_platform.schema_manager` fuera de este alcance).

Depende de `client` (sin hacer ninguna request) solo para activar el parche de
`db.get_session` -> `db_session` que arma `tests/conftest.py`: sin él, la sesión que
abre el propio background task no vería lo que este test insertó en la misma
transacción."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app_platform.notifications.models.notification_model import NotificationModel
from receivables.reports.background_tasks import execute_and_notify
from receivables.reports.schemas.report_schemas import ReportExecuteRequest


async def _notifications_for(db_session, user_id: uuid.UUID) -> list[NotificationModel]:
    result = await db_session.execute(
        select(NotificationModel).where(NotificationModel.user_id == user_id).order_by(NotificationModel.created_at.desc())
    )
    return list(result.scalars().all())


class TestExecuteAndNotify:
    async def test_success_creates_success_notification(self, client, db_session, real_admin_user_id):
        report_id = uuid.uuid4()
        org_id = uuid.uuid4()
        fake_result = {
            "success": True,
            "rows": 3,
            "columns": ["a"],
            "data": [{"a": 1}],
            "mode": "audit",
            "file_name": "reporte.csv",
            "document_id": uuid.uuid4(),
        }
        with patch(
            "receivables.reports.background_tasks.ReportService.execute", AsyncMock(return_value=fake_result)
        ):
            await execute_and_notify(report_id, org_id, ReportExecuteRequest(mode="audit"), real_admin_user_id)

        notifications = await _notifications_for(db_session, real_admin_user_id)
        assert len(notifications) == 1
        assert notifications[0].title == "Reporte generado"
        assert notifications[0].notif_type == "success"
        assert "reporte.csv" in notifications[0].body

    async def test_http_exception_creates_error_notification(self, client, db_session, real_admin_user_id):
        report_id = uuid.uuid4()
        org_id = uuid.uuid4()
        with patch(
            "receivables.reports.background_tasks.ReportService.execute",
            AsyncMock(side_effect=HTTPException(422, "config inválida")),
        ):
            await execute_and_notify(report_id, org_id, ReportExecuteRequest(mode="audit"), real_admin_user_id)

        notifications = await _notifications_for(db_session, real_admin_user_id)
        assert len(notifications) == 1
        assert notifications[0].title == "Error al generar reporte"
        assert notifications[0].notif_type == "error"

    async def test_generic_exception_creates_error_notification(self, client, db_session, real_admin_user_id):
        report_id = uuid.uuid4()
        org_id = uuid.uuid4()
        with patch(
            "receivables.reports.background_tasks.ReportService.execute",
            AsyncMock(side_effect=ValueError("boom inesperado")),
        ):
            await execute_and_notify(report_id, org_id, ReportExecuteRequest(mode="audit"), real_admin_user_id)

        notifications = await _notifications_for(db_session, real_admin_user_id)
        assert len(notifications) == 1
        assert notifications[0].title == "Error al generar reporte"
        assert notifications[0].notif_type == "error"

    async def test_session_used_is_isolated_per_call_but_sees_test_data(
        self, client, db_session, real_admin_user_id
    ):
        """El propio background task abre su sesión con `db.get_session()` -- sin el
        parche de `tests/conftest.py` (`db.get_session = _bg_session_override`), esta
        llamada abriría otra conexión real y `real_admin_user_id` (insertado en la
        transacción de `db_session`, no comiteado) le resultaría inexistente ->
        ForeignKeyViolationError en vez de terminar limpio."""
        with patch(
            "receivables.reports.background_tasks.ReportService.execute",
            AsyncMock(return_value={"success": True, "rows": 0, "file_name": "x.csv", "document_id": None}),
        ):
            await execute_and_notify(uuid.uuid4(), uuid.uuid4(), ReportExecuteRequest(mode="audit"), real_admin_user_id)

        notifications = await _notifications_for(db_session, real_admin_user_id)
        assert len(notifications) == 1
