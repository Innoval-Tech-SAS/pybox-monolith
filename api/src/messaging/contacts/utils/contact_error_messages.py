import re

from sqlalchemy.exc import IntegrityError


def duplicate_contact_message(error: IntegrityError) -> str:
    error_text = str(error.orig)
    match = re.search(r"Key \((?P<column>[^)]+)\)=\((?P<value>[^)]+)\)", error_text)

    if not match:
        return "Ya existe un contacto con el mismo correo electrónico o número de teléfono."

    column_names = {
        "correo_electronico": "correo electrónico",
        "numero_telefono": "número de teléfono",
    }
    column = column_names.get(match.group("column"), "dato")
    value = match.group("value")

    return f"Ya existe un contacto registrado con el {column}: {value}."
