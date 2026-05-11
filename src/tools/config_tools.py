import os


def get_or_throw(key: str) -> str:

    assert key, "La clave no puede estar vacía."

    value = os.getenv(key)
    if value is None:
        raise RuntimeError(f"Variable de entorno '{key}' no encontrada.")
    return value
