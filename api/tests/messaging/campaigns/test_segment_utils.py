"""Tests puros de `segment_utils.py`: resolver la columna del id de deudor en las
filas crudas que devuelve el DML (varía según haya joins o no) y extraer ids
únicos y válidos de esas filas.
"""

import uuid

from messaging.campaigns.utils.segment_utils import debtor_id_column, extract_debtor_ids


class TestDebtorIdColumn:
    def test_single_table_deudores_uses_raw_id(self):
        criteria = {"tables": [{"name": "deudores"}]}
        assert debtor_id_column(criteria) == "id"

    def test_multi_table_with_deudores_uses_alias_suffix(self):
        criteria = {"tables": [{"name": "deudores", "alias": "d"}, {"name": "creditos", "alias": "c"}]}
        assert debtor_id_column(criteria) == "d_id"

    def test_multi_table_without_alias_uses_table_name_suffix(self):
        criteria = {"tables": [{"name": "deudores"}, {"name": "creditos"}]}
        assert debtor_id_column(criteria) == "deudores_id"

    def test_no_deudores_table_and_multi_table_defaults_to_deudores_id(self):
        criteria = {"tables": [{"name": "creditos"}, {"name": "pagos"}]}
        assert debtor_id_column(criteria) == "deudores_id"

    def test_no_deudores_table_and_single_table_defaults_to_id(self):
        criteria = {"tables": [{"name": "creditos"}]}
        assert debtor_id_column(criteria) == "id"

    def test_empty_tables_defaults_to_id(self):
        assert debtor_id_column({"tables": []}) == "id"
        assert debtor_id_column({}) == "id"

    def test_qualified_table_name_uses_last_segment(self):
        criteria = {"tables": [{"name": "public.deudores", "alias": "dd"}, {"name": "creditos"}]}
        assert debtor_id_column(criteria) == "dd_id"


class TestExtractDebtorIds:
    def test_extracts_unique_valid_uuids_preserving_order(self):
        id1, id2 = uuid.uuid4(), uuid.uuid4()
        rows = [{"id": str(id1)}, {"id": str(id2)}, {"id": str(id1)}]
        result = extract_debtor_ids(rows, {"tables": [{"name": "deudores"}]})
        assert result == [id1, id2]

    def test_rows_with_missing_column_are_skipped(self):
        valid_id = uuid.uuid4()
        rows = [{"other_col": "x"}, {"id": str(valid_id)}]
        result = extract_debtor_ids(rows, {"tables": [{"name": "deudores"}]})
        assert result == [valid_id]

    def test_rows_with_invalid_uuid_are_skipped(self):
        valid_id = uuid.uuid4()
        rows = [{"id": "not-a-uuid"}, {"id": str(valid_id)}]
        result = extract_debtor_ids(rows, {"tables": [{"name": "deudores"}]})
        assert result == [valid_id]

    def test_rows_with_falsy_value_are_skipped(self):
        valid_id = uuid.uuid4()
        rows = [{"id": None}, {"id": ""}, {"id": str(valid_id)}]
        result = extract_debtor_ids(rows, {"tables": [{"name": "deudores"}]})
        assert result == [valid_id]

    def test_empty_rows_returns_empty_list(self):
        assert extract_debtor_ids([], {"tables": [{"name": "deudores"}]}) == []

    def test_multi_table_uses_aliased_column(self):
        debtor_id = uuid.uuid4()
        criteria = {"tables": [{"name": "deudores", "alias": "d"}, {"name": "creditos", "alias": "c"}]}
        rows = [{"d_id": str(debtor_id), "c_id": str(uuid.uuid4())}]
        assert extract_debtor_ids(rows, criteria) == [debtor_id]
