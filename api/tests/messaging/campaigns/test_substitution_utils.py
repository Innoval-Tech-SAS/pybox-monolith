"""Tests puros de `substitution_utils.py`: aplanado de valores para el payload
``sub`` que espera 360nrs. El bug real que evita ``build_sub`` (ver comentario
en el archivo) es envolver los valores en un dict anidado -- 360nrs responde 500
si eso pasa, así que se prueba explícitamente la forma plana del resultado.
"""

from enum import Enum

from messaging.campaigns.utils.substitution_utils import build_sub, stringify_value


class _Suit(Enum):
    HEARTS = "corazones"


class TestStringifyValue:
    def test_none_becomes_empty_string(self):
        assert stringify_value(None) == ""

    def test_enum_uses_its_value_not_repr(self):
        assert stringify_value(_Suit.HEARTS) == "corazones"

    def test_number_is_stringified(self):
        assert stringify_value(42) == "42"
        assert stringify_value(3.5) == "3.5"

    def test_string_passthrough(self):
        assert stringify_value("ya texto") == "ya texto"


class TestBuildSub:
    def test_none_data_returns_none(self):
        assert build_sub(None) is None

    def test_empty_dict_returns_none(self):
        assert build_sub({}) is None

    def test_returns_flat_list_with_single_dict_not_nested_under_values(self):
        result = build_sub({"nombre": "Ana", "monto": 1500})
        # Forma plana esperada por 360nrs: [{"nombre": "Ana", "monto": "1500"}] -- NUNCA
        # [{"values": {...}}], que es justo el bug que causaba el 500 documentado arriba.
        assert result == [{"nombre": "Ana", "monto": "1500"}]
        assert "values" not in result[0]

    def test_none_values_in_data_become_empty_strings(self):
        result = build_sub({"nombre": "Ana", "apellido": None})
        assert result == [{"nombre": "Ana", "apellido": ""}]

    def test_enum_values_are_stringified_by_their_value(self):
        result = build_sub({"palo": _Suit.HEARTS})
        assert result == [{"palo": "corazones"}]
