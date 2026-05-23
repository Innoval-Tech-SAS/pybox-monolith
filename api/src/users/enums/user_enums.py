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


VALID_ROLE_SCOPE: set[tuple[UserRole, UserScope]] = {
    (UserRole.ADMIN,             UserScope.GLOBAL),
    (UserRole.CUSTOMER_SERVICE,  UserScope.GLOBAL),
    (UserRole.ADMIN,             UserScope.ORGANIZATION),
    (UserRole.CUSTOMER_SERVICE,  UserScope.ORGANIZATION),
    (UserRole.USER_ORGANIZATION, UserScope.ORGANIZATION),
    (UserRole.USER,              UserScope.SELF),
}
