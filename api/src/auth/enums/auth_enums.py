from enum import Enum


class AuthProvider(str, Enum):
    GOOGLE = "GOOGLE"
    SELF = "SELF"
