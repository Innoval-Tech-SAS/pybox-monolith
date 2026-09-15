"""Tests contra DB real (sin pasar por HTTP) para `DmlService`, el ejecutor del
query-builder dinámico de segmentos/reportes. Cubre los tipos de filtro más comunes
(igualdad, IN, rango de fechas, contiene) y el rechazo de tablas fuera del allowlist
`TENANT_SCOPED_TABLES` cuando se pide scoping por portafolio/organización.
"""

import json
import uuid
from datetime import datetime, timedelta, timezone

from app_platform.schema_manager.services.dml_service import DmlService


class TestExecuteQueryFilters:
    async def test_equality_filter(self, db_session):
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[{"name": "paises", "columns": ["codigo", "nombre"], "filters": [
                {"column": "codigo", "op": "=", "value": "CO"}
            ]}],
        )
        assert result["success"] is True
        rows = json.loads(result["data"])
        assert len(rows) == 1
        assert rows[0]["codigo"] == "CO"

    async def test_in_filter(self, db_session):
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[{"name": "paises", "columns": ["codigo"], "filters": [
                {"column": "codigo", "op": "in", "value": ["CO", "MX"]}
            ]}],
        )
        assert result["success"] is True
        rows = json.loads(result["data"])
        codes = {r["codigo"] for r in rows}
        assert codes <= {"CO", "MX"}
        assert len(rows) >= 1

    async def test_contains_filter_via_ilike(self, db_session):
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[{"name": "paises", "columns": ["codigo", "nombre"], "filters": [
                {"column": "nombre", "op": "ilike", "value": "%colomb%"}
            ]}],
        )
        assert result["success"] is True
        rows = json.loads(result["data"])
        assert any(r["codigo"] == "CO" for r in rows)

    async def test_date_range_filter_between(self, db_session):
        # `fecha_creacion` la puebla el seed al arrancar la sesión de test: un rango
        # amplio alrededor de "ahora" debe capturar todos los países sembrados.
        service = DmlService(db_session)
        start = (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat()
        end = (datetime.now(timezone.utc) + timedelta(days=1)).date().isoformat()
        result = await service.execute_query(
            tables=[{"name": "paises", "columns": ["codigo"], "filters": [
                {"column": "fecha_creacion", "op": "between", "value": [start, end]}
            ]}],
        )
        assert result["success"] is True
        assert result["rows"] >= 5

    async def test_no_matching_rows_still_succeeds(self, db_session):
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[{"name": "paises", "columns": ["codigo"], "filters": [
                {"column": "codigo", "op": "=", "value": "ZZ"}
            ]}],
        )
        assert result["success"] is True
        assert result["rows"] == 0

    async def test_invalid_identifier_in_filter_column_fails_gracefully(self, db_session):
        # `execute_query` atrapa el ValueError de sanitización y responde success=False
        # en vez de dejar que el error suba: nunca interpola el identificador crudo.
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[{"name": "paises", "columns": ["codigo"], "filters": [
                {"column": "codigo; DROP TABLE paises; --", "op": "=", "value": "CO"}
            ]}],
        )
        assert result["success"] is False
        assert result["error"]

    async def test_no_tables_fails_gracefully(self, db_session):
        service = DmlService(db_session)
        result = await service.execute_query(tables=[])
        assert result["success"] is False
        assert "table is required" in result["error"]


class TestExecuteQueryTenantScope:
    async def test_table_outside_allowlist_rejected(self, db_session):
        # `paises` no está en TENANT_SCOPED_TABLES: pedir scoping por portafolio sobre
        # ella debe fallar, no ignorarse silenciosamente.
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[{"name": "paises", "columns": ["codigo"]}],
            portfolio_ids=[uuid.uuid4()],
            organization_ids=[],
        )
        assert result["success"] is False
        assert "no está habilitada" in result["error"]

    async def test_allowlisted_table_with_no_matching_portfolio_returns_zero_rows(self, db_session):
        # `creditos` sí está en el allowlist: con un portfolio_id que no existe, la
        # condición de scoping se aplica y no debe devolver ninguna fila (ni tampoco
        # fallar por construir mal el SQL).
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[{"name": "creditos", "columns": ["id"]}],
            portfolio_ids=[uuid.uuid4()],
            organization_ids=[],
        )
        assert result["success"] is True
        assert result["rows"] == 0

    async def test_no_scoping_when_ids_are_none(self, db_session):
        # Sin portfolio_ids/organization_ids no se aplica ningún WHERE de scoping: el
        # caller (database_controller) solo pasa así cuando ya gateó a admin global.
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[{"name": "paises", "columns": ["codigo"]}],
        )
        assert result["success"] is True
        assert result["rows"] >= 5
