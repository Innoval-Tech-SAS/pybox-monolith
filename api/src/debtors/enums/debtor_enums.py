from enum import Enum


class DebtorType(str, Enum):
    DEBTOR = "Titular"
    CO_DEBTOR = "Co-deudor"


class DocumentTypes(str, Enum):
    CC = "Cédula de Ciudadanía"
    CE = "Cédula de Extranjería"
    CI = "Cédula de Identidad"
    NIT = "Número de Identificación Tributaria"
    PASSPORT = "Pasaporte"
    DNI = "Documento Nacional de Identidad"
