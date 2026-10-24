"""Tests de extract_variable_slots (ver whatsapp_template_parser.py), función pura
que parsea variables nombradas ({{nombre}}) de los componentes BODY/HEADER que
Meta devuelve para una plantilla."""

from messaging.whatsapp.utils.whatsapp_template_parser import extract_variable_slots


class TestExtractVariableSlots:
    def test_extracts_named_variables_from_body(self):
        components = [{"type": "BODY", "text": "Hola {{nombre}}, debes {{monto}}"}]

        slots = extract_variable_slots(components)

        assert [(s.component, s.name) for s in slots] == [
            ("BODY", "nombre"),
            ("BODY", "monto"),
        ]

    def test_ignores_footer_and_buttons_components(self):
        components = [
            {"type": "FOOTER", "text": "{{no_deberia_salir}}"},
            {"type": "BUTTONS", "buttons": [{"text": "{{tampoco}}"}]},
        ]

        assert extract_variable_slots(components) == []

    def test_header_and_body_both_contribute_slots(self):
        components = [
            {"type": "HEADER", "text": "Recordatorio para {{nombre}}"},
            {"type": "BODY", "text": "Tu saldo es {{monto}}"},
        ]

        slots = extract_variable_slots(components)

        assert [(s.component, s.name) for s in slots] == [
            ("HEADER", "nombre"),
            ("BODY", "monto"),
        ]

    def test_lowercase_type_is_normalized_to_uppercase(self):
        components = [{"type": "body", "text": "Hola {{nombre}}"}]

        slots = extract_variable_slots(components)

        assert slots[0].component == "BODY"

    def test_component_without_variables_is_skipped(self):
        components = [{"type": "BODY", "text": "Texto fijo sin variables"}]

        assert extract_variable_slots(components) == []

    def test_missing_text_field_is_tolerated(self):
        components = [{"type": "BODY"}]

        assert extract_variable_slots(components) == []

    def test_duplicate_variable_appears_only_once_preserving_first_order(self):
        components = [
            {
                "type": "BODY",
                "text": "{{nombre}} repetido {{monto}} y otra vez {{nombre}}",
            }
        ]

        slots = extract_variable_slots(components)

        assert [s.name for s in slots] == ["nombre", "monto"]

    def test_fills_example_from_named_params_when_present(self):
        components = [
            {
                "type": "BODY",
                "text": "Hola {{nombre}}, debes {{monto}}",
                "example": {
                    "body_text_named_params": [
                        {"param_name": "nombre", "example": "Juan"},
                        {"param_name": "monto", "example": "150000"},
                    ]
                },
            }
        ]

        slots = extract_variable_slots(components)

        assert {s.name: s.example for s in slots} == {
            "nombre": "Juan",
            "monto": "150000",
        }

    def test_header_example_uses_header_text_named_params_key(self):
        components = [
            {
                "type": "HEADER",
                "text": "Hola {{nombre}}",
                "example": {
                    "header_text_named_params": [
                        {"param_name": "nombre", "example": "Ana"}
                    ]
                },
            }
        ]

        slots = extract_variable_slots(components)

        assert slots[0].example == "Ana"

    def test_variable_without_matching_example_defaults_to_empty_string(self):
        components = [
            {
                "type": "BODY",
                "text": "Hola {{nombre}}",
                "example": {
                    "body_text_named_params": [{"param_name": "otro", "example": "x"}]
                },
            }
        ]

        slots = extract_variable_slots(components)

        assert slots[0].example == ""

    def test_positional_style_variables_are_not_matched(self):
        """El formato forzado al crear (parameter_format=NAMED) es {{nombre}}, no
        {{1}} posicional -- un nombre que empieza por dígito no matchea el patrón."""
        components = [{"type": "BODY", "text": "Hola {{1}}"}]

        assert extract_variable_slots(components) == []

    def test_empty_components_list_returns_empty(self):
        assert extract_variable_slots([]) == []
