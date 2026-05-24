from enum import Enum


class VerificationChannel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
