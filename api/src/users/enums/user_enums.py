from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMINISTRADOR"
    CUSTOMER_SERVICE = "ATENCION AL CLIENTE"
    USER_ORGANIZATION = "USUARIO ORGANIZACIÓN"


class UserScope(str, Enum):
    ORGANIZATION = "ORGANIZATION"
    GLOBAL = "GLOBAL"
    SELF = "SELF"


class UserDocumentType(str, Enum):
    CC = "CÉDULA DE CIUDADANÍA"
    CE = "CÉDULA DE EXTRANJERÍA"
    PASSPORT = "PASAPORTE"
    NIT = "NIT"
    PEP = "PERMISO ESPECIAL DE PERMANENCIA"
