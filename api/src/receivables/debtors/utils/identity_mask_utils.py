import re

from receivables.debtors.constants.debtor_identity_constants import (
    EMAIL_VISIBLE_CHARS,
    MASK_CHAR,
    PHONE_COMPARE_DIGITS,
    PHONE_MIN_DIGITS,
    PHONE_VISIBLE_DIGITS,
)


def mask_email(email: str) -> str:
    """Oculta un correo dejando visibles los 2 primeros caracteres y lo que sigue
    al último punto.

    ``dev.innovaltect@gmail.com`` -> ``de*************@*****.com``. Con una parte
    local muy corta se deja visible menos, para que siempre quede algo oculto.
    """
    local, _, domain = email.partition("@")
    visible = min(EMAIL_VISIBLE_CHARS, max(len(local) - 1, 0))
    masked_local = local[:visible] + MASK_CHAR * (len(local) - visible)

    name, dot, suffix = domain.rpartition(".")
    masked_domain = (
        MASK_CHAR * len(name) + dot + suffix if dot else MASK_CHAR * len(domain)
    )
    return f"{masked_local}@{masked_domain}"


def mask_phone(phone: str) -> str:
    """Oculta un teléfono dejando visibles solo sus últimos dígitos (nunca más de
    la mitad)."""
    digits = digits_only(phone)
    visible = min(PHONE_VISIBLE_DIGITS, len(digits) // 2)
    return MASK_CHAR * (len(digits) - visible) + digits[len(digits) - visible :]


def digits_only(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def phone_compare_key(value: str) -> str | None:
    """Clave de comparación de un teléfono (sus últimos dígitos); ``None`` si es
    muy corto."""
    digits = digits_only(value)
    if len(digits) < PHONE_MIN_DIGITS:
        return None
    return digits[-PHONE_COMPARE_DIGITS:]
