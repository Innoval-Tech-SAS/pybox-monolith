"""Tests de `TemplateRenderer` (sustitución local `{variable}` usada solo por el
endpoint de preview, ver template_renderer.py -- el envío real delega la sustitución
a NRS360 vía `sub`). Riesgo real: una variable sin valor en el diccionario no debe
desaparecer del texto (se deja el placeholder tal cual, para que el usuario note el
dato faltante en la vista previa), y `find_variables` debe deduplicar nombres
repetidos.
"""

from messaging.templates.services.template_renderer import TemplateRenderer


class TestFindVariables:
    def test_finds_all_distinct_variable_names(self):
        renderer = TemplateRenderer()
        found = renderer.find_variables(
            "Hola {nombre}, tu saldo es {saldo}. {nombre}, no lo olvides."
        )
        assert found == {"nombre", "saldo"}

    def test_no_variables_returns_empty_set(self):
        renderer = TemplateRenderer()
        assert renderer.find_variables("texto sin variables") == set()


class TestRender:
    def test_substitutes_known_variable(self):
        renderer = TemplateRenderer()
        assert renderer.render("Hola {nombre}", {"nombre": "Ana"}) == "Hola Ana"

    def test_missing_variable_keeps_placeholder_unchanged(self):
        renderer = TemplateRenderer()
        assert renderer.render("Hola {nombre}", {}) == "Hola {nombre}"

    def test_non_string_value_is_stringified(self):
        renderer = TemplateRenderer()
        assert renderer.render("Cuota #{numero}", {"numero": 3}) == "Cuota #3"


class TestRenderFields:
    def test_renders_body_and_subject_together(self):
        renderer = TemplateRenderer()
        body, subject = renderer.render_fields(
            "Hola {nombre}", "Recordatorio para {nombre}", {"nombre": "Ana"}
        )
        assert body == "Hola Ana"
        assert subject == "Recordatorio para Ana"

    def test_none_subject_renders_as_empty_string(self):
        renderer = TemplateRenderer()
        body, subject = renderer.render_fields("Hola {nombre}", None, {"nombre": "Ana"})
        assert subject == ""


class TestSingletonInstance:
    def test_new_always_returns_the_same_instance(self):
        assert TemplateRenderer() is TemplateRenderer()
