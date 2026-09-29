from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import DeclarativeBase


def column_attr_map(model_class: type[DeclarativeBase]) -> dict[str, str]:
    """Mapea nombre de columna en BD -> atributo Python del modelo (ej.
    'nombre_completo' -> 'full_name')."""
    return {
        column.name: attr for attr, column in sa_inspect(model_class).columns.items()
    }
