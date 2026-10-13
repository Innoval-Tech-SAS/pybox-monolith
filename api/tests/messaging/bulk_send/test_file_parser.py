"""Tests de `parse_file` (parseo del CSV/XLSX cargado para envío masivo, ver
file_parser.py). Riesgos reales: columnas obligatorias faltantes o archivo vacío no
deben producir un traceback de polars sino un 422 legible; un archivo que excede el
límite de filas/tamaño se corta antes de intentar parsear el resto; y todas las
columnas terminan como string (incluidos nulos, que se rellenan con "") para que
`BulkSendService` no reciba `None` donde espera `str`.
"""

import io

import pytest
from fastapi import HTTPException, UploadFile

from messaging.bulk_send.utils.file_parser import parse_file


def make_upload_file(
    content: bytes, filename: str = "contactos.csv", content_type: str = "text/csv"
) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=io.BytesIO(content),
        headers={"content-type": content_type},
    )


class TestParseFileRequiredColumns:
    async def test_missing_required_columns_raises_422_with_column_names(self):
        csv = "documento,destinatario\n123,3001112233\n"
        file = make_upload_file(csv.encode("utf-8"))

        with pytest.raises(HTTPException) as exc_info:
            await parse_file(file)

        assert exc_info.value.status_code == 422
        assert "tipo_documento" in exc_info.value.detail

    async def test_all_required_columns_present_parses_successfully(self):
        csv = "tipo_documento,documento,destinatario\nCC,123,3001112233\n"
        file = make_upload_file(csv.encode("utf-8"))

        rows = await parse_file(file)

        assert rows == [
            {"tipo_documento": "CC", "documento": "123", "destinatario": "3001112233"}
        ]


class TestParseFileEmptyOrOversized:
    async def test_header_only_csv_raises_422_no_data_rows(self):
        csv = "tipo_documento,documento,destinatario\n"
        file = make_upload_file(csv.encode("utf-8"))

        with pytest.raises(HTTPException) as exc_info:
            await parse_file(file)

        assert exc_info.value.status_code == 422
        assert "no contiene filas" in exc_info.value.detail

    async def test_file_over_size_limit_raises_413(self):
        oversized = b"a" * (10 * 1024 * 1024 + 1)
        file = make_upload_file(oversized)

        with pytest.raises(HTTPException) as exc_info:
            await parse_file(file)

        assert exc_info.value.status_code == 413

    async def test_row_count_over_limit_raises_422(self):
        header = "tipo_documento,documento,destinatario\n"
        rows = "".join(f"CC,{i},300111{i:04d}\n" for i in range(10_001))
        file = make_upload_file((header + rows).encode("utf-8"))

        with pytest.raises(HTTPException) as exc_info:
            await parse_file(file)

        assert exc_info.value.status_code == 422
        assert "10000 filas" in exc_info.value.detail


class TestParseFileMissingCellData:
    async def test_row_with_missing_optional_cell_is_filled_with_empty_string(self):
        # `documento` vacío en la 2a fila (fila con datos faltantes) -- no debe romper
        # el parseo ni dejar un `None` en el dict resultante.
        csv = (
            "tipo_documento,documento,destinatario\nCC,123,3001112233\nCC,,3001112244\n"
        )
        file = make_upload_file(csv.encode("utf-8"))

        rows = await parse_file(file)

        assert len(rows) == 2
        assert rows[1]["documento"] == ""
        assert all(isinstance(v, str) for row in rows for v in row.values())

    async def test_extra_column_beyond_required_is_preserved_for_template_variables(
        self,
    ):
        csv = "tipo_documento,documento,destinatario,nombre\nCC,123,3001112233,Ana\n"
        file = make_upload_file(csv.encode("utf-8"))

        rows = await parse_file(file)

        assert rows[0]["nombre"] == "Ana"


class TestParseFileMalformedContent:
    async def test_malformed_csv_raises_422_instead_of_raw_parser_error(self):
        # Comillas sin cerrar: polars no puede tokenizar el archivo.
        malformed = b'tipo_documento,documento,destinatario\n"CC,123,3001112233\n'
        file = make_upload_file(malformed)

        with pytest.raises(HTTPException) as exc_info:
            await parse_file(file)

        assert exc_info.value.status_code == 422

    async def test_xlsx_extension_routes_to_excel_reader_and_rejects_csv_bytes(self):
        # Contenido CSV real pero con extensión .xlsx: el lector de Excel debe fallar
        # limpio (422), no reventar con una excepción cruda de openpyxl/calamine.
        csv = b"tipo_documento,documento,destinatario\nCC,123,3001112233\n"
        file = make_upload_file(
            csv, filename="contactos.xlsx", content_type="application/octet-stream"
        )

        with pytest.raises(HTTPException) as exc_info:
            await parse_file(file)

        assert exc_info.value.status_code == 422
