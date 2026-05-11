from io import BytesIO

import polars as pl
from werkzeug.datastructures import FileStorage

from ..repositories.contact_repository import ContactRepository


class ContactServices:

    def __init__(self):
        self.repository = ContactRepository()

    def process_file(self, file: FileStorage, type_file: str):
        required_columns = {"email", "phone_number"}
        batch_size = 1000
        file_bytes = file.read()

        if not file_bytes:
            raise ValueError("El archivo está vacío")

        if type_file == "csv":
            df = pl.read_csv(BytesIO(file_bytes))
        elif type_file == "xlsx":
            df = pl.read_excel(file_bytes)
        else:
            raise RuntimeError(
                "Archivo no permitido. Solo se aceptan archivos .csv o .xlsx"
            )

        columns = set(df.columns)

        if not required_columns.issubset(columns):
            missing_columns = required_columns - columns

            raise ValueError(
                f"El archivo debe contener las siguientes columnas: {', '.join(missing_columns)}"
            )

        extra_info_columns = columns - required_columns

        if extra_info_columns:
            print(f"Columnas adicionales encontradas: {', '.join(extra_info_columns)}")

        total_saved = 0
        total_skipped = 0
        batch = []

        for row in df.to_dicts():
            email = row.get("email")
            phone_number = row.get("phone_number")

            if isinstance(email, str):
                email = email.strip() or None

            if isinstance(phone_number, str):
                phone_number = phone_number.strip() or None

            if not email and not phone_number:
                total_skipped += 1
                continue

            extra_info = {
                col: row[col] for col in extra_info_columns if row.get(col) is not None
            }

            contact_data = {
                "email": email,
                "phone_number": phone_number,
                "extra_info": extra_info if extra_info else None,
            }

            contact = self.repository.model_class(**contact_data)
            batch.append(contact)

            if len(batch) >= batch_size:
                saved_contacts = self.repository.add_many(batch)
                total_saved += len(saved_contacts)
                batch.clear()

        if batch:
            saved_contacts = self.repository.add_many(batch)
            total_saved += len(saved_contacts)

        return {
            "total_saved": total_saved,
            "total_skipped": total_skipped,
            "extra_info_columns": list(extra_info_columns),
        }
