from enum import Enum


class AuthProvider(str, Enum):
    GOOGLE = "GOOGLE"
    FACEBOOK = "FACEBOOK"
    SELF = "SELF"
