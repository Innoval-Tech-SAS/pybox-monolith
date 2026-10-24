"""Tests de `TemplateVariableService.list_available_variables` (ver
template_variable_service.py). Riesgos reales: un campo técnico (`id_credito`) de
`deudores`/`creditos` no debe filtrarse a la lista; una misma clave descubierta en dos
tablas debe quedarse con la primera (no duplicarse); y cada columna de `pagos` debe
expandirse en una variable por estrategia de cuota (ver PAYMENT_STRATEGY_SUFFIXES),
no en una sola variable ambigua.

Unitario puro: `InspectorService` va mockeado -- no hay introspección real de schema.
"""

from unittest.mock import AsyncMock, MagicMock

from messaging.campaigns.constants import PAYMENT_STRATEGY_SUFFIXES, PAYMENT_TABLE
from messaging.templates.services.template_variable_service import (
    TemplateVariableService,
)


def build_service(*, deudores=None, creditos=None, pagos=None):
    inspector = MagicMock()

    async def _get_table_fields(schema, table):
        return {
            "deudores": deudores or [],
            "creditos": creditos or [],
            PAYMENT_TABLE: pagos or [],
        }[table]

    inspector.get_table_fields = AsyncMock(side_effect=_get_table_fields)
    return TemplateVariableService(inspector), inspector


class TestListAvailableVariablesHidesTechnicalFields:
    async def test_id_field_from_source_table_is_excluded(self):
        service, _ = build_service(
            deudores=[
                {"name": "id_credito", "type": "uuid"},
                {"name": "nombre_completo", "type": "varchar"},
            ]
        )

        variables = await service.list_available_variables()

        keys = {v.key for v in variables}
        assert "id_credito" not in keys
        assert "nombre_completo" in keys


class TestListAvailableVariablesDeduplicates:
    async def test_same_column_name_in_two_tables_keeps_first_occurrence(self):
        service, _ = build_service(
            deudores=[{"name": "nombre_completo", "type": "varchar"}],
            creditos=[{"name": "nombre_completo", "type": "text"}],
        )

        variables = await service.list_available_variables()

        matches = [v for v in variables if v.key == "nombre_completo"]
        assert len(matches) == 1
        assert matches[0].source_table == "deudores"


class TestListAvailableVariablesExpandsPaymentStrategies:
    async def test_payment_column_generates_one_variable_per_strategy_suffix(self):
        service, _ = build_service(pagos=[{"name": "saldo_cuota", "type": "numeric"}])

        variables = await service.list_available_variables()

        keys = {v.key for v in variables}
        expected_keys = {
            f"saldo_cuota_{suffix}" for suffix in PAYMENT_STRATEGY_SUFFIXES
        }
        assert expected_keys.issubset(keys)
        assert len(expected_keys) == len(PAYMENT_STRATEGY_SUFFIXES)

    async def test_hidden_payment_column_is_excluded_from_all_strategies(self):
        service, _ = build_service(pagos=[{"name": "id_pago", "type": "uuid"}])

        variables = await service.list_available_variables()

        assert not any(v.key.startswith("id_pago") for v in variables)


class TestListAvailableVariablesSortedByKey:
    async def test_result_is_sorted_alphabetically_by_key(self):
        service, _ = build_service(
            deudores=[
                {"name": "zapato", "type": "varchar"},
                {"name": "apellido", "type": "varchar"},
            ]
        )

        variables = await service.list_available_variables()

        keys = [v.key for v in variables]
        assert keys == sorted(keys)
