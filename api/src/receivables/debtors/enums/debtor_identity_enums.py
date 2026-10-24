"""Canal de verificación de identidad del deudor."""

from enum import StrEnum


class IdentityChannel(StrEnum):
    """Dato con el que el titular confirma que es quien dice ser."""

    EMAIL = "EMAIL"
    PHONE = "PHONE"
