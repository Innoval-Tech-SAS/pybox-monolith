"""Construcción del `sub` (personalización) en el formato que espera 360NRS."""

from enum import Enum
from typing import Any


def stringify_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def build_sub(data: dict[str, Any] | None) -> list[dict[str, Any]] | None:
    if not data:
        return None
    # 360nrs espera cada elemento de ``sub`` como un dict plano de
    # variable→valor, alineado posicionalmente al ``to`` (igual que el
    # envío OTP: ``[{"code": "..."}]``).
    # Envolverlo en ``{"values": {...}}`` hacía que 360nrs recibiera un objeto anidado
    # como valor de sustitución y respondiera 500 code=101 "Internal Database error".
    return [{key: stringify_value(value) for key, value in data.items()}]
