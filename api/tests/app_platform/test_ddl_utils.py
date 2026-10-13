"""Unit tests puros para las utilidades de DDL dinámico (creación/alteración de
columnas de segmentos). Cubren el render seguro de DEFAULT y la construcción del
DDL de columna, incluyendo el rechazo de identificadores inválidos."""

import pytest

from app_platform.schema_manager.schemas.database_schemas import (
    ColumnDataType,
    ColumnDefinition,
)
from app_platform.schema_manager.utils.ddl_utils import (
    build_column_ddl,
    build_column_type,
    render_default_value,
    validate_ident,
)


class TestValidateIdent:
    def test_valid_identifier(self):
        assert validate_ident("mi_columna", "column name") == "mi_columna"

    def test_invalid_identifier_raises(self):
        with pytest.raises(ValueError, match="Identificador inválido"):
            validate_ident("not a valid ident!", "column name")

    def test_sql_injection_attempt_rejected(self):
        with pytest.raises(ValueError):
            validate_ident("x; DROP TABLE usuarios; --", "table name")


class TestRenderDefaultValue:
    def test_safe_keyword_uppercased(self):
        assert render_default_value("current_timestamp") == "CURRENT_TIMESTAMP"

    def test_safe_function_keyword(self):
        assert render_default_value("now()") == "NOW()"

    def test_numeric_literal_unescaped(self):
        assert render_default_value("42") == "42"

    def test_negative_numeric_literal(self):
        assert render_default_value("-3.5") == "-3.5"

    def test_arbitrary_text_treated_as_literal_and_escaped(self):
        assert render_default_value("hello") == "'hello'"

    def test_text_with_quote_is_escaped(self):
        assert render_default_value("O'Brien") == "'O''Brien'"

    def test_sql_injection_attempt_becomes_a_harmless_string_literal(self):
        # Un intento de inyección no calza con keyword seguro ni con el regex
        # numérico, así que cae al escapado de string: queda inerte como literal.
        rendered = render_default_value("1; DROP TABLE usuarios; --")
        assert rendered == "'1; DROP TABLE usuarios; --'"


class TestBuildColumnType:
    def test_varchar_with_length(self):
        col = ColumnDefinition(name="x", data_type=ColumnDataType.VARCHAR, length=50)
        assert build_column_type(col) == "VARCHAR(50)"

    def test_varchar_without_length_falls_back_to_bare_type(self):
        col = ColumnDefinition(name="x", data_type=ColumnDataType.VARCHAR, length=0)
        assert build_column_type(col) == "VARCHAR"

    def test_char_with_length(self):
        col = ColumnDefinition(name="x", data_type=ColumnDataType.CHAR, length=1)
        assert build_column_type(col) == "CHAR(1)"

    def test_numeric_with_precision_and_scale(self):
        col = ColumnDefinition(
            name="x", data_type=ColumnDataType.NUMERIC, precision=10, scale=2
        )
        assert build_column_type(col) == "NUMERIC(10,2)"

    def test_numeric_with_precision_only(self):
        col = ColumnDefinition(name="x", data_type=ColumnDataType.NUMERIC, precision=10)
        assert build_column_type(col) == "NUMERIC(10)"

    def test_numeric_without_precision_falls_back_to_bare_type(self):
        col = ColumnDefinition(name="x", data_type=ColumnDataType.NUMERIC)
        assert build_column_type(col) == "NUMERIC"

    def test_simple_type_passthrough(self):
        col = ColumnDefinition(name="x", data_type=ColumnDataType.INTEGER)
        assert build_column_type(col) == "INTEGER"

    def test_double_precision_type(self):
        col = ColumnDefinition(name="x", data_type=ColumnDataType.DOUBLE)
        assert build_column_type(col) == "DOUBLE PRECISION"


class TestBuildColumnDdl:
    def test_basic_nullable_text_column(self):
        col = ColumnDefinition(name="etiqueta", data_type=ColumnDataType.TEXT)
        assert build_column_ddl(col) == '"etiqueta" TEXT'

    def test_not_null_column(self):
        col = ColumnDefinition(
            name="etiqueta", data_type=ColumnDataType.TEXT, nullable=False
        )
        assert build_column_ddl(col) == '"etiqueta" TEXT NOT NULL'

    def test_primary_key_omits_not_null(self):
        col = ColumnDefinition(
            name="id",
            data_type=ColumnDataType.INTEGER,
            primary_key=True,
            nullable=False,
        )
        assert build_column_ddl(col) == '"id" INTEGER PRIMARY KEY'

    def test_unique_column(self):
        col = ColumnDefinition(
            name="codigo", data_type=ColumnDataType.TEXT, unique=True
        )
        assert build_column_ddl(col) == '"codigo" TEXT UNIQUE'

    def test_column_with_default_value(self):
        col = ColumnDefinition(
            name="activo", data_type=ColumnDataType.BOOLEAN, default_value="true"
        )
        assert build_column_ddl(col) == '"activo" BOOLEAN DEFAULT TRUE'

    def test_varchar_column_with_length_and_default(self):
        col = ColumnDefinition(
            name="estado",
            data_type=ColumnDataType.VARCHAR,
            length=20,
            default_value="pendiente",
        )
        assert build_column_ddl(col) == "\"estado\" VARCHAR(20) DEFAULT 'pendiente'"

    def test_invalid_column_name_rejected(self):
        col = ColumnDefinition(
            name="bad name; DROP TABLE x", data_type=ColumnDataType.TEXT
        )
        with pytest.raises(ValueError, match="Identificador inválido"):
            build_column_ddl(col)
