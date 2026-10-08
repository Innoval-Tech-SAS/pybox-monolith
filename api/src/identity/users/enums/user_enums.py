"""Rol, scope y estado de verificación de identidad de un usuario."""

from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMINISTRADOR"
    CUSTOMER_SERVICE = "ATENCION_AL_CLIENTE"
    USER = "USUARIO"


class UserScope(str, Enum):
    ORGANIZATION = "ORGANIZACION"
    GLOBAL = "GLOBAL"
    SELF = "PROPIO"


class PermissionEffect(str, Enum):
    GRANT = "OTORGAR"
    REVOKE = "REVOCAR"


class IdentityVerificationStatus(str, Enum):
    """Estado de verificación de identidad de un usuario SELF (titular). Gatea el
    acceso a su información crediticia (/credits/my-credits, /statements/my-statements,
    /judicial-notifications/mine): conocer el tipo+número de documento de alguien no
    debería bastar para ver sus obligaciones, así que además de existir como deudor,
    el titular debe subir su documento de identidad y que Atención al Cliente lo
    apruebe (ticket de soporte, categoría validación de identidad)."""

    NOT_SUBMITTED = "NO_ENVIADO"
    PENDING = "PENDIENTE"
    APPROVED = "APROBADO"
    DENIED = "DENEGADO"


VALID_ROLE_SCOPE: set[tuple[UserRole, UserScope]] = {
    (UserRole.ADMIN, UserScope.GLOBAL),
    (UserRole.CUSTOMER_SERVICE, UserScope.GLOBAL),
    (UserRole.ADMIN, UserScope.ORGANIZATION),
    (UserRole.CUSTOMER_SERVICE, UserScope.ORGANIZATION),
    (UserRole.USER, UserScope.ORGANIZATION),
    (UserRole.USER, UserScope.SELF),
}
