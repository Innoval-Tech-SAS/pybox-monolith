"""Normalización de valores de contacto (email/teléfono) para comparar y guardar."""

import re

from receivables.contact_methods.enums.contact_method_enums import ContactMethodType


def normalize_email(value: str) -> str:
    """Normaliza un correo para comparación/almacenamiento: sin espacios y en
    minúsculas."""
    return (value or "").strip().lower()


def normalize_phone(value: str, country_prefix: str | None) -> str:
    """Antepone el indicativo de país (solo dígitos) al número si no lo trae ya.

    Deja solo dígitos en ambos (quita ``+``, espacios, guiones). Un número local se
    devuelve como ``{indicativo}{numero}``; si ya venía con el indicativo se respeta.
    Sin indicativo disponible se devuelve el valor con solo dígitos.

    Réplica intencional de ``messaging.campaigns.utils.provider_utils.normalize_phone``
    para no crear una dependencia inversa de ``receivables`` hacia ``messaging``.
    """
    digits = re.sub(r"\D", "", value or "")
    code = re.sub(r"\D", "", country_prefix or "")
    if not digits:
        return ""
    if not code:
        return digits
    # Un número local de la región tiene ≤10 dígitos; si ya trae más y arranca con el
    # indicativo, se asume normalizado y no se vuelve a prefijar.
    if digits.startswith(code) and len(digits) > 10:
        return digits
    return f"{code}{digits}"


def normalize_contact_value(
    contact_type: ContactMethodType, value: str, country_prefix: str | None
) -> str:
    """Normaliza un valor de contacto según su tipo (EMAIL → minúsculas; PHONE → con
    prefijo)."""
    if contact_type == ContactMethodType.PHONE:
        return normalize_phone(value, country_prefix)
    return normalize_email(value)
