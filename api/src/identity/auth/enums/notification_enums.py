"""Canal por el que se envía el código de verificación (OTP)."""

from enum import StrEnum


class VerificationChannel(StrEnum):
    EMAIL = "EMAIL"
    SMS = "SMS"
