from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMINISTRADOR"
    CUSTOMER_SERVICE = "ATENCION AL CLIENTE"
    USER_ORGANIZATION = "USUARIO ORGANIZACIÓN"
    USER = "USUARIO"


class UserScope(str, Enum):
    ORGANIZATION = "ORGANIZATION"
    GLOBAL = "GLOBAL"
    SELF = "SELF"


class PermissionEffect(str, Enum):
    GRANT = "GRANT"
    REVOKE = "REVOKE"
