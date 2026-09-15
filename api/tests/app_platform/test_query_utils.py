"""Unit tests puros (sin DB) para el query-builder dinámico de segmentos/reportes.

`query_utils.py` es el módulo crítico de sanitización: todo identificador que termina
en SQL crudo (columnas, tablas, alias) pasa por acá antes de interpolarse en el
string de la query. Estos tests cubren la construcción de condiciones para los
filtros comunes (igualdad, IN, BETWEEN, LIKE/contiene) y que un identificador
inválido se rechaza antes de llegar a componerse en SQL.
"""

import pytest

from app_platform.schema_manager.utils.query_utils import (
    build_sql_condition,
    build_table_alias_map,
    build_tenant_scope_condition,
    build_where_clauses,
    is_aggregate_mode,
    normalize_aggregate_specs,
    normalize_operator,
    resolve_alias,
    resolve_full_table_name,
    sanitize_identifier,
    sanitize_table_name,
    sql_literal,
)


class TestSanitizeIdentifier:
    def test_valid_identifier_passes_through(self):
        assert sanitize_identifier("nombre_columna", label="column") == "nombre_columna"

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="required"):
            sanitize_identifier("", label="column")

    def test_none_raises(self):
        with pytest.raises(ValueError, match="required"):
            sanitize_identifier(None, label="column")

    @pytest.mark.parametrize(
        "bad",
        [
            "not a valid ident!",
            "1starts_with_digit",
            "drop table x; --",
            "col-with-dash",
            "col;DROP TABLE usuarios",
            "col.with.dots",
        ],
    )
    def test_invalid_identifier_rejected(self, bad):
        with pytest.raises(ValueError, match="Invalid"):
            sanitize_identifier(bad, label="column")


class TestSanitizeTableName:
    def test_without_schema_defaults_to_public(self):
        assert sanitize_table_name("creditos") == ("public", "creditos")

    def test_with_schema(self):
        assert sanitize_table_name("reportes.creditos") == ("reportes", "creditos")

    def test_invalid_table_rejected(self):
        with pytest.raises(ValueError):
            sanitize_table_name("creditos; DROP TABLE usuarios")

    def test_invalid_schema_rejected(self):
        with pytest.raises(ValueError):
            sanitize_table_name("bad schema!.creditos")


class TestSqlLiteral:
    def test_none_is_null(self):
        assert sql_literal(None) == "NULL"

    def test_bool(self):
        assert sql_literal(True) == "TRUE"
        assert sql_literal(False) == "FALSE"

    def test_number(self):
        assert sql_literal(42) == "42"
        assert sql_literal(3.5) == "3.5"

    def test_string_escapes_quotes(self):
        assert sql_literal("O'Brien") == "'O''Brien'"


class TestBuildSqlCondition:
    def test_equality(self):
        assert build_sql_condition("t.col", "=", "CO") == "t.col = 'CO'"

    def test_not_equal_uses_diamond(self):
        assert build_sql_condition("t.col", "!=", 1) == "t.col <> 1"

    def test_in_operator(self):
        cond = build_sql_condition("t.col", "in", ["CO", "MX"])
        assert cond == "t.col IN ('CO', 'MX')"

    def test_in_operator_single_value_wraps_in_list(self):
        assert build_sql_condition("t.col", "in", "CO") == "t.col IN ('CO')"

    def test_in_operator_empty_list_raises(self):
        with pytest.raises(ValueError, match="IN operator"):
            build_sql_condition("t.col", "in", [])

    def test_not_in_operator(self):
        assert build_sql_condition("t.col", "not_in", ["CO"]) == "t.col NOT IN ('CO')"

    def test_between_date_range(self):
        cond = build_sql_condition("t.fecha", "between", ["2024-01-01", "2024-12-31"])
        assert cond == "t.fecha BETWEEN '2024-01-01' AND '2024-12-31'"

    def test_between_requires_exactly_two_values(self):
        with pytest.raises(ValueError, match="two values"):
            build_sql_condition("t.fecha", "between", ["2024-01-01"])

    def test_like_contains(self):
        assert build_sql_condition("t.nombre", "like", "%Colombia%") == "t.nombre LIKE '%Colombia%'"

    def test_ilike_contains_case_insensitive(self):
        assert build_sql_condition("t.nombre", "ilike", "%colombia%") == "t.nombre ILIKE '%colombia%'"

    def test_is_null(self):
        assert build_sql_condition("t.col", "is_null", None) == "t.col IS NULL"

    def test_is_not_null(self):
        assert build_sql_condition("t.col", "is_not_null", None) == "t.col IS NOT NULL"

    def test_greater_than(self):
        assert build_sql_condition("t.monto", ">", 1000) == "t.monto > 1000"


class TestNormalizeOperator:
    def test_aliases_normalize(self):
        assert normalize_operator("eq") == "="
        assert normalize_operator("notIn") == "not_in"
        assert normalize_operator(" GTE ") == ">="

    def test_default_is_equals(self):
        assert normalize_operator("") == "="
        assert normalize_operator(None) == "="


class TestBuildWhereClauses:
    def test_empty_filters_returns_empty_string(self):
        assert build_where_clauses([], "t") == ""

    def test_single_equality_filter(self):
        clause = build_where_clauses([{"column": "codigo", "op": "=", "value": "CO"}], "t")
        assert clause == "t.codigo = 'CO'"

    def test_multiple_filters_joined_with_and(self):
        clause = build_where_clauses(
            [
                {"column": "codigo", "op": "=", "value": "CO"},
                {"column": "activo", "op": "=", "value": True},
            ],
            "t",
        )
        assert clause == "t.codigo = 'CO' AND t.activo = TRUE"

    def test_in_filter(self):
        clause = build_where_clauses([{"column": "codigo", "op": "in", "value": ["CO", "MX"]}], "t")
        assert clause == "t.codigo IN ('CO', 'MX')"

    def test_between_filter_date_range(self):
        clause = build_where_clauses(
            [{"column": "fecha", "op": "between", "value": ["2024-01-01", "2024-12-31"]}], "t"
        )
        assert clause == "t.fecha BETWEEN '2024-01-01' AND '2024-12-31'"

    def test_contains_filter_via_ilike(self):
        clause = build_where_clauses([{"column": "nombre", "op": "ilike", "value": "%bogo%"}], "t")
        assert clause == "t.nombre ILIKE '%bogo%'"

    def test_invalid_column_rejected(self):
        with pytest.raises(ValueError):
            build_where_clauses([{"column": "bad col!", "op": "=", "value": 1}], "t")

    def test_invalid_operator_rejected(self):
        with pytest.raises(ValueError, match="Invalid operator"):
            build_where_clauses([{"column": "codigo", "op": "; DROP TABLE x", "value": 1}], "t")


class TestBuildTenantScopeCondition:
    def test_allowlisted_table_builds_condition(self):
        cond = build_tenant_scope_condition("public.creditos", "c", [], [])
        assert "c.id_portafolio IN (NULL)" in cond

    def test_allowlisted_table_with_ids(self):
        import uuid

        pid = uuid.uuid4()
        cond = build_tenant_scope_condition("public.creditos", "c", [pid], [])
        assert str(pid) in cond

    def test_table_outside_allowlist_rejected(self):
        with pytest.raises(ValueError, match="no está habilitada"):
            build_tenant_scope_condition("public.usuarios", "u", [], [])

    def test_table_outside_allowlist_rejected_even_for_valid_table_name(self):
        # `paises` es una tabla real del esquema pero no está en TENANT_SCOPED_TABLES:
        # reportes/segmentos no pueden apuntarle.
        with pytest.raises(ValueError):
            build_tenant_scope_condition("public.paises", "p", [], [])


class TestBuildTableAliasMap:
    def test_default_alias_is_table_name(self):
        alias_map = build_table_alias_map([{"name": "creditos"}])
        assert alias_map == {"public.creditos": "creditos"}

    def test_explicit_alias(self):
        alias_map = build_table_alias_map([{"name": "creditos", "alias": "c"}])
        assert alias_map == {"public.creditos": "c"}

    def test_duplicate_alias_rejected(self):
        with pytest.raises(ValueError, match="Duplicate table alias"):
            build_table_alias_map(
                [{"name": "creditos", "alias": "x"}, {"name": "deudores", "alias": "x"}]
            )


class TestResolveAlias:
    def test_single_table_no_ref_needed(self):
        tables = [{"name": "creditos"}]
        assert resolve_alias(tables, None) == "creditos"

    def test_multiple_tables_requires_ref(self):
        tables = [{"name": "creditos"}, {"name": "deudores"}]
        with pytest.raises(ValueError, match="required"):
            resolve_alias(tables, None)

    def test_resolve_by_alias(self):
        tables = [{"name": "creditos", "alias": "c"}, {"name": "deudores", "alias": "d"}]
        assert resolve_alias(tables, "d") == "d"

    def test_unknown_reference_rejected(self):
        tables = [{"name": "creditos"}]
        with pytest.raises(ValueError, match="Unknown table reference"):
            resolve_alias(tables, "does_not_exist")


class TestResolveFullTableName:
    def test_single_table(self):
        tables = [{"name": "creditos"}]
        assert resolve_full_table_name(tables, None) == "public.creditos"

    def test_by_alias(self):
        tables = [{"name": "creditos", "alias": "c"}]
        assert resolve_full_table_name(tables, "c") == "public.creditos"


class TestIsAggregateMode:
    def test_explicit_aggregate_mode(self):
        assert is_aggregate_mode("aggregate", [], [], [], []) is True

    def test_detail_mode_without_group_by_is_not_aggregate(self):
        assert is_aggregate_mode("detail", [], [], [], []) is False

    def test_group_by_implies_aggregate(self):
        assert is_aggregate_mode("detail", [{"column": "x"}], [], [], []) is True


class TestNormalizeAggregateSpecs:
    def test_count_star(self):
        tables = [{"name": "creditos", "alias": "c"}]
        result = normalize_aggregate_specs(
            tables, [], [{"function": "count", "column": "*"}], [], []
        )
        assert result["aggregations"][0]["sql_expression"] == "COUNT(*)"

    def test_sum_column_on_table(self):
        tables = [{"name": "creditos", "alias": "c"}]
        result = normalize_aggregate_specs(
            tables, [], [{"function": "sum", "column": "monto"}], [], []
        )
        assert result["aggregations"][0]["sql_expression"] == "SUM(c.monto)"

    def test_star_with_non_count_function_rejected(self):
        tables = [{"name": "creditos", "alias": "c"}]
        with pytest.raises(ValueError, match="Only COUNT"):
            normalize_aggregate_specs(tables, [], [{"function": "sum", "column": "*"}], [], [])

    def test_no_aggregations_rejected(self):
        tables = [{"name": "creditos", "alias": "c"}]
        with pytest.raises(ValueError, match="At least one aggregation"):
            normalize_aggregate_specs(tables, [], [], [], [])

    def test_having_references_unknown_metric_rejected(self):
        tables = [{"name": "creditos", "alias": "c"}]
        with pytest.raises(ValueError, match="Unknown metric alias"):
            normalize_aggregate_specs(
                tables,
                [],
                [{"function": "count", "column": "*"}],
                [{"metric": "nope", "op": ">", "value": 1}],
                [],
            )

    def test_order_by_must_reference_group_or_metric_alias(self):
        tables = [{"name": "creditos", "alias": "c"}]
        with pytest.raises(ValueError, match="order_by field"):
            normalize_aggregate_specs(
                tables,
                [],
                [{"function": "count", "column": "*"}],
                [],
                [{"field": "not_an_alias", "direction": "asc"}],
            )

    def test_duplicated_output_alias_rejected(self):
        tables = [{"name": "creditos", "alias": "c"}]
        with pytest.raises(ValueError, match="Duplicated output alias"):
            normalize_aggregate_specs(
                tables,
                [{"column": "estado", "alias": "same"}],
                [{"function": "count", "column": "*", "alias": "same"}],
                [],
                [],
            )
