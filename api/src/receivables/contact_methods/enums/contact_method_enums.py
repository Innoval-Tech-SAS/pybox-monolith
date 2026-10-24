"""Tipo de método de contacto de un deudor (email o teléfono)."""

from enum import StrEnum


class ContactMethodType(StrEnum):
    EMAIL = "EMAIL"
    PHONE = "TELEFONO"
