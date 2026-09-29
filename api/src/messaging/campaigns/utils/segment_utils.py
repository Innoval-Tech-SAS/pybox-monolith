import uuid
from typing import Any


def debtor_id_column(criteria: dict[str, Any]) -> str:
    """Nombre de la columna que trae el id del deudor en las filas del segmento.

    El DML prefija con el alias de la tabla cuando hay joins (``deudores_id``) y usa el
    nombre crudo cuando la consulta es de una sola tabla (``id``).
    """
    tables = criteria.get("tables") or []
    multi = len(tables) > 1
    for table in tables:
        name = str(table.get("name") or "").rsplit(".", maxsplit=1)[-1]
        if name == "deudores":
            alias = table.get("alias") or name
            return f"{alias}_id" if multi else "id"
    return "deudores_id" if multi else "id"


def extract_debtor_ids(rows: list[dict], criteria: dict[str, Any]) -> list[uuid.UUID]:
    """Ids de deudor únicos de las filas del segmento, preservando el orden
    de la consulta.

    Las filas que no traen un UUID válido en la columna del deudor se descartan.
    """
    column = debtor_id_column(criteria)
    debtor_ids: list[uuid.UUID] = []
    seen: set[uuid.UUID] = set()
    for row in rows:
        raw = row.get(column)
        if not raw:
            continue
        try:
            debtor_id = uuid.UUID(str(raw))
        except ValueError:
            continue
        if debtor_id not in seen:
            seen.add(debtor_id)
            debtor_ids.append(debtor_id)
    return debtor_ids
