from dataclasses import dataclass
from io import BytesIO
from typing import Any

import polars as pl
from werkzeug.datastructures import FileStorage


@dataclass(frozen=True)
class ContactFileData:
    contacts: list[dict[str, Any]]
    total_skipped: int
    extra_info_columns: list[str]


class ContactFileParser:
    REQUIRED_COLUMNS = {"email", "phone_number"}

    def parse(self, file: FileStorage, type_file: str) -> ContactFileData:
        file_bytes = file.read()

        if not file_bytes:
            raise ValueError("El archivo está vacío")

        df = self._read_dataframe(file_bytes, type_file)
        columns = set(df.columns)
        self._validate_columns(columns)

        extra_info_columns = sorted(columns - self.REQUIRED_COLUMNS)

        if extra_info_columns:
            print(f"Columnas adicionales encontradas: {', '.join(extra_info_columns)}")

        contacts = []
        total_skipped = 0

        for row in df.to_dicts():
            contact_data = self._build_contact_data(row, extra_info_columns)

            if contact_data is None:
                total_skipped += 1
                continue

            contacts.append(contact_data)

        return ContactFileData(
            contacts=contacts,
            total_skipped=total_skipped,
            extra_info_columns=extra_info_columns,
        )

    def _read_dataframe(self, file_bytes: bytes, type_file: str) -> pl.DataFrame:
        if type_file == "csv":
            return pl.read_csv(BytesIO(file_bytes))

        if type_file == "xlsx":
            return pl.read_excel(file_bytes)

        raise RuntimeError("Archivo no permitido. Solo se aceptan archivos .csv o .xlsx")

    def _validate_columns(self, columns: set[str]) -> None:
        if self.REQUIRED_COLUMNS.issubset(columns):
            return

        missing_columns = self.REQUIRED_COLUMNS - columns
        raise ValueError(
            f"El archivo debe contener las siguientes columnas: {', '.join(missing_columns)}"
        )

    def _build_contact_data(
        self, row: dict[str, Any], extra_info_columns: list[str]
    ) -> dict[str, Any] | None:
        email = self._clean_value(row.get("email"))
        phone_number = self._clean_value(row.get("phone_number"))

        if not email and not phone_number:
            return None

        extra_info = {
            col: row[col] for col in extra_info_columns if row.get(col) is not None
        }

        return {
            "email": email,
            "phone_number": phone_number,
            "extra_info": extra_info if extra_info else None,
        }

    def _clean_value(self, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip() or None

        return value
