import re

MIN_LENGTH = 8
_CLASS_PATTERNS = (
    re.compile(r"[a-z]"),
    re.compile(r"[A-Z]"),
    re.compile(r"\d"),
    re.compile(r"[^a-zA-Z0-9]"),
)


def validate_password_strength(password: str) -> str:
    """Exige longitud mínima y al menos 3 de 4 clases de carácter (minúscula,
    mayúscula, dígito, símbolo). Usado como field_validator en los schemas de
    registro/cambio/reset de contraseña."""
    if len(password) < MIN_LENGTH:
        raise ValueError(f"La contraseña debe tener al menos {MIN_LENGTH} caracteres.")
    classes_present = sum(1 for pattern in _CLASS_PATTERNS if pattern.search(password))
    if classes_present < 3:
        raise ValueError(
            "La contraseña debe combinar al menos 3 de: minúsculas, mayúsculas, números y símbolos."
        )
    return password
