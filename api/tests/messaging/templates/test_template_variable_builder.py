"""Tests de las funciones puras que arman las variables de plantilla disponibles a
partir de columnas de BD (ver template_variable_builder.py). Riesgo real: un campo
técnico (`id`, `*_id`, columnas de auditoría) filtrándose al editor de plantillas
como si fuera una variable de negocio, y el `example_for` eligiendo un ejemplo
genérico cuando existe uno mejor por nombre o tipo de dato.
"""

from messaging.templates.utils.template_variable_builder import (
    build_payment_variable,
    build_variable,
    example_for,
    is_audit_field,
    is_id_field,
    should_hide_field,
    to_human_label,
)


class TestIsIdField:
    def test_bare_id_is_id_field(self):
        assert is_id_field("id") is True

    def test_prefixed_id_field(self):
        assert is_id_field("id_portafolio") is True

    def test_suffixed_id_field(self):
        assert is_id_field("portafolio_id") is True

    def test_id_in_middle_of_name_is_id_field(self):
        assert is_id_field("id_deudor_hash") is True

    def test_unrelated_field_is_not_id_field(self):
        assert is_id_field("identificacion") is False

    def test_saldo_field_is_not_id_field(self):
        assert is_id_field("saldo_total") is False


class TestIsAuditField:
    def test_creation_date_is_audit_field(self):
        assert is_audit_field("fecha_creacion") is True

    def test_case_insensitive(self):
        assert is_audit_field("FECHA_CREACION") is True

    def test_regular_field_is_not_audit_field(self):
        assert is_audit_field("nombre_completo") is False


class TestShouldHideField:
    def test_hides_id_fields(self):
        assert should_hide_field("id_portafolio") is True

    def test_hides_audit_fields(self):
        assert should_hide_field("eliminado_en") is True

    def test_does_not_hide_business_field(self):
        assert should_hide_field("saldo_total") is False


class TestToHumanLabel:
    def test_replaces_underscores_and_capitalizes_first_letter(self):
        assert to_human_label("nombre_completo") == "Nombre completo"

    def test_empty_string_returns_empty_string(self):
        assert to_human_label("") == ""


class TestExampleFor:
    def test_matches_keyword_before_falling_back_to_type(self):
        assert example_for("nombre_completo", "varchar") == "Juan Pérez"

    def test_boolean_type_without_keyword_match(self):
        assert example_for("activo", "boolean") == "true"

    def test_time_field_with_hora_keyword_uses_time_example(self):
        assert example_for("hora_pago", "time") == "14:30:00"

    def test_date_field_without_hora_keyword_uses_date_example(self):
        assert example_for("fecha_pago", "date") == "2025-11-14"

    def test_integer_type_uses_numeric_example(self):
        assert example_for("plazo_meses", "integer") == "123"

    def test_monetary_keyword_with_numeric_type_uses_money_example(self):
        assert example_for("saldo_capital", "numeric") == "1234.56"

    def test_generic_numeric_type_without_monetary_keyword(self):
        assert example_for("porcentaje_avance", "numeric") == "12.34"

    def test_dias_keyword_without_recognized_type_uses_count_example(self):
        assert example_for("dias_mora", "unknown") == "35"

    def test_unrecognized_field_and_type_falls_back_to_generic(self):
        assert example_for("campo_raro", "unknown") == "Ejemplo"


class TestBuildVariable:
    def test_hidden_field_returns_none(self):
        assert build_variable("id_deudor", "uuid", "deudores") is None

    def test_visible_field_returns_option_with_expected_shape(self):
        option = build_variable("nombre_completo", "varchar", "deudores")
        assert option is not None
        assert option.key == "nombre_completo"
        assert option.label == "Nombre completo"
        assert option.example == "Juan Pérez"
        assert option.source_table == "deudores"


class TestBuildPaymentVariable:
    def test_hidden_field_returns_none(self):
        assert (
            build_payment_variable(
                "id_pago", "uuid", "proxima", "Próxima cuota", "pagos"
            )
            is None
        )

    def test_key_and_label_include_strategy_suffix(self):
        option = build_payment_variable(
            "saldo_cuota", "numeric", "proxima", "Próxima cuota", "pagos"
        )
        assert option is not None
        assert option.key == "saldo_cuota_proxima"
        assert option.label == "Saldo cuota (Próxima cuota)"
        assert option.source_table == "pagos"
