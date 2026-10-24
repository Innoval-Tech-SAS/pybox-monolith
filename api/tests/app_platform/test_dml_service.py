"""Tests contra DB real (sin pasar por HTTP) para `DmlService`, el ejecutor del
query-builder dinámico de segmentos/reportes. Cubre los tipos de filtro más comunes
(igualdad, IN, rango de fechas, contiene) y el rechazo de tablas fuera del allowlist
`TENANT_SCOPED_TABLES` cuando se pide scoping por portafolio/organización.
"""

import json
import uuid
from datetime import datetime, timedelta, timezone

from app_platform.schema_manager.services.dml_service import DmlService
from core.security.services.encrypt_service import encrypt_service
from tests.receivables.conftest import (
    build_credit,
    build_debtor,
    build_organization,
    build_portfolio,
)


class TestExecuteQueryFilters:
    async def test_equality_filter(self, db_session):
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[
                {
                    "name": "paises",
                    "columns": ["codigo", "nombre"],
                    "filters": [{"column": "codigo", "op": "=", "value": "CO"}],
                }
            ],
        )
        assert result["success"] is True
        rows = json.loads(result["data"])
        assert len(rows) == 1
        assert rows[0]["codigo"] == "CO"

    async def test_in_filter(self, db_session):
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[
                {
                    "name": "paises",
                    "columns": ["codigo"],
                    "filters": [
                        {"column": "codigo", "op": "in", "value": ["CO", "MX"]}
                    ],
                }
            ],
        )
        assert result["success"] is True
        rows = json.loads(result["data"])
        codes = {r["codigo"] for r in rows}
        assert codes <= {"CO", "MX"}
        assert len(rows) >= 1

    async def test_contains_filter_via_ilike(self, db_session):
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[
                {
                    "name": "paises",
                    "columns": ["codigo", "nombre"],
                    "filters": [
                        {"column": "nombre", "op": "ilike", "value": "%colomb%"}
                    ],
                }
            ],
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
            tables=[
                {
                    "name": "paises",
                    "columns": ["codigo"],
                    "filters": [
                        {
                            "column": "fecha_creacion",
                            "op": "between",
                            "value": [start, end],
                        }
                    ],
                }
            ],
        )
        assert result["success"] is True
        assert result["rows"] >= 5

    async def test_no_matching_rows_still_succeeds(self, db_session):
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[
                {
                    "name": "paises",
                    "columns": ["codigo"],
                    "filters": [{"column": "codigo", "op": "=", "value": "ZZ"}],
                }
            ],
        )
        assert result["success"] is True
        assert result["rows"] == 0

    async def test_invalid_identifier_in_filter_column_fails_gracefully(
        self, db_session
    ):
        # `execute_query` atrapa el ValueError de sanitización y responde success=False
        # en vez de dejar que el error suba: nunca interpola el identificador crudo.
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[
                {
                    "name": "paises",
                    "columns": ["codigo"],
                    "filters": [
                        {
                            "column": "codigo; DROP TABLE paises; --",
                            "op": "=",
                            "value": "CO",
                        }
                    ],
                }
            ],
        )
        assert result["success"] is False
        assert result["error"]

    async def test_no_tables_fails_gracefully(self, db_session):
        service = DmlService(db_session)
        result = await service.execute_query(tables=[])
        assert result["success"] is False
        assert "al menos una tabla" in result["error"]


class TestExecuteQueryErrorReporting:
    """Cada tipo de fallo responde con un mensaje que dice qué corregir, con el código
    HTTP que corresponde, y sin filtrar el SQL (lleva el scope de tenant)."""

    async def test_unknown_column_reports_which_column(self, db_session):
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[{"name": "paises", "columns": ["no_existe"]}]
        )
        assert result["success"] is False
        assert result["status_code"] == 422
        assert "no existe" in result["error"]
        assert "no_existe" in result["error"]
        assert "SELECT" not in result["error"]

    async def test_unknown_table_is_user_error(self, db_session):
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[{"name": "tabla_que_no_existe", "columns": ["id"]}]
        )
        assert result["success"] is False
        assert result["status_code"] == 422
        assert "tablas configuradas no existe" in result["error"]
        assert "SELECT" not in result["error"]

    async def test_invalid_date_value_reports_format_problem(self, db_session):
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[
                {
                    "name": "paises",
                    "columns": ["codigo"],
                    "filters": [
                        {
                            "column": "fecha_creacion",
                            "op": "=",
                            "value": "no-es-una-fecha",
                        }
                    ],
                }
            ],
        )
        assert result["success"] is False
        assert result["status_code"] == 422
        assert "fecha u hora" in result["error"]
        assert "SELECT" not in result["error"]

    async def test_join_without_right_table_reports_missing_field(self, db_session):
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[
                {"name": "paises", "columns": ["codigo"]},
                {"name": "creditos", "columns": ["id"]},
            ],
            joins=[{"left": "paises", "left_on": "id", "right_on": "id"}],
        )
        assert result["success"] is False
        assert result["status_code"] == 422
        assert "'right'" in result["error"]

    async def test_join_with_empty_columns_asks_for_them_in_spanish(self, db_session):
        # El wizard permite guardar un join con las columnas vacías: se corrige editándolo.
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[
                {"name": "deudores", "columns": ["id"]},
                {"name": "creditos", "columns": ["id"]},
            ],
            joins=[
                {
                    "left": "deudores",
                    "right": "creditos",
                    "left_on": "",
                    "right_on": "",
                    "how": "inner",
                }
            ],
        )
        assert result["success"] is False
        assert result["status_code"] == 422
        assert result["error"] == "Falta indicar la columna izquierda del join."

    async def test_duplicate_table_alias_is_reported_in_spanish(self, db_session):
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[
                {"name": "creditos", "alias": "creditos", "columns": ["id"]},
                {"name": "deudores", "alias": "creditos", "columns": ["id"]},
            ],
            joins=[
                {
                    "left": "creditos",
                    "right": "deudores",
                    "left_on": "id_deudor",
                    "right_on": "id",
                    "how": "inner",
                }
            ],
        )
        assert result["success"] is False
        assert result["status_code"] == 422
        assert "'creditos' está repetido" in result["error"]

    async def test_multiple_tables_without_joins_asks_for_joins_in_spanish(
        self, db_session
    ):
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[
                {"name": "deudores", "columns": ["id"]},
                {"name": "creditos", "columns": ["id"]},
            ],
        )
        assert result["success"] is False
        assert result["status_code"] == 422
        assert (
            result["error"]
            == "Se requieren uniones (joins) cuando hay más de una tabla."
        )

    async def test_validation_error_is_user_error(self, db_session):
        service = DmlService(db_session)
        result = await service.execute_query(tables=[])
        assert result["success"] is False
        assert result["status_code"] == 422

    async def test_document_number_filter_by_hash_executes(self, db_session):
        # Regresión del incidente: `numero_documento = 6168564922` (varchar = bigint).
        service = DmlService(db_session)
        result = await service.execute_query(
            tables=[
                {
                    "name": "deudores",
                    "columns": ["id"],
                    "filters": [
                        {"column": "numero_documento", "op": "=", "value": "6168564922"}
                    ],
                }
            ],
        )
        assert result["success"] is True
        assert result["rows"] == 0


class TestRowsToDicts:
    """Serialización del resultado: descifrado solo de las columnas pedidas."""

    def test_decrypts_only_requested_columns(self):
        token = encrypt_service.encrypt_to_str("6168564922")
        data = DmlService._rows_to_dicts(
            ["nombre", "documento"], [("Ana", token)], {"documento"}
        )
        assert data == [{"nombre": "Ana", "documento": "6168564922"}]

    def test_leaves_token_untouched_when_column_not_requested(self):
        token = encrypt_service.encrypt_to_str("6168564922")
        data = DmlService._rows_to_dicts(["documento"], [(token,)], set())
        assert data == [{"documento": token}]

    def test_undecryptable_value_becomes_none_instead_of_failing(self):
        data = DmlService._rows_to_dicts(
            ["documento"], [("v1:corrupto:corrupto:corrupto",)], {"documento"}
        )
        assert data == [{"documento": None}]


class TestExecuteQueryDecryptSensitive:
    """De punta a punta contra la DB: filtro por hash + documento descifrado."""

    @staticmethod
    async def _debtor_in_portfolio(db_session, document: str):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        debtor = build_debtor(org.id, document_number_plain=document)
        db_session.add(debtor)
        await db_session.flush()
        db_session.add(build_credit(portfolio.id, debtor.id))
        await db_session.flush()
        return org, portfolio

    async def test_single_table_returns_plain_document_when_requested(self, db_session):
        document = f"{uuid.uuid4().int % 10**10:010d}"
        org, portfolio = await self._debtor_in_portfolio(db_session, document)
        result = await DmlService(db_session).execute_query(
            tables=[
                {
                    "name": "deudores",
                    "columns": ["numero_documento"],
                    "filters": [
                        {"column": "numero_documento", "op": "=", "value": document}
                    ],
                }
            ],
            portfolio_ids=[portfolio.id],
            organization_ids=[org.id],
            decrypt_sensitive=True,
        )
        assert result["success"] is True
        assert json.loads(result["data"]) == [{"numero_documento": document}]

    async def test_document_stays_encrypted_by_default(self, db_session):
        document = f"{uuid.uuid4().int % 10**10:010d}"
        org, portfolio = await self._debtor_in_portfolio(db_session, document)
        result = await DmlService(db_session).execute_query(
            tables=[
                {
                    "name": "deudores",
                    "columns": ["numero_documento"],
                    "filters": [
                        {"column": "numero_documento", "op": "=", "value": document}
                    ],
                }
            ],
            portfolio_ids=[portfolio.id],
            organization_ids=[org.id],
        )
        assert result["success"] is True
        (row,) = json.loads(result["data"])
        assert row["numero_documento"].startswith("v1:")
        assert document not in row["numero_documento"]

    async def test_join_returns_plain_document_under_prefixed_column(self, db_session):
        document = f"{uuid.uuid4().int % 10**10:010d}"
        org, portfolio = await self._debtor_in_portfolio(db_session, document)
        result = await DmlService(db_session).execute_query(
            tables=[
                {
                    "name": "deudores",
                    "alias": "deudores",
                    "columns": ["numero_documento"],
                    "filters": [
                        {"column": "numero_documento", "op": "=", "value": document}
                    ],
                },
                {
                    "name": "creditos",
                    "alias": "creditos",
                    "columns": ["numero_credito"],
                },
            ],
            joins=[
                {
                    "left": "deudores",
                    "right": "creditos",
                    "left_on": "id",
                    "right_on": "id_deudor",
                    "how": "inner",
                }
            ],
            portfolio_ids=[portfolio.id],
            organization_ids=[org.id],
            decrypt_sensitive=True,
        )
        assert result["success"] is True
        (row,) = json.loads(result["data"])
        assert row["deudores_numero_documento"] == document


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

    async def test_allowlisted_table_with_no_matching_portfolio_returns_zero_rows(
        self, db_session
    ):
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
