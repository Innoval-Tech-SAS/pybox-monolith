from enum import Enum


class Nationality(str, Enum):
    CO = "CO"
    MX = "MX"
    AR = "AR"
    PE = "PE"
    VE = "VE"


class UserDocumentType(str, Enum):
    # Colombia
    CC = "CC"
    CE = "CE"
    NIT = "NIT"
    PEP = "PEP"
    # México
    CURP = "CURP"
    INE = "INE"
    RFC = "RFC"
    # Argentina
    DNI = "DNI"
    CUIL = "CUIL"
    CUIT = "CUIT"
    # Perú
    RUC = "RUC"
    # Venezuela
    CI = "CI"
    RIF = "RIF"
    # Universal
    PASSPORT = "PASSPORT"


DOCUMENTS_BY_NATIONALITY: dict["Nationality", list["UserDocumentType"]] = {
    Nationality.CO: [
        UserDocumentType.CC,
        UserDocumentType.CE,
        UserDocumentType.NIT,
        UserDocumentType.PEP,
        UserDocumentType.PASSPORT,
    ],
    Nationality.MX: [
        UserDocumentType.CURP,
        UserDocumentType.INE,
        UserDocumentType.RFC,
        UserDocumentType.PASSPORT,
    ],
    Nationality.AR: [
        UserDocumentType.DNI,
        UserDocumentType.CUIL,
        UserDocumentType.CUIT,
        UserDocumentType.PASSPORT,
    ],
    Nationality.PE: [
        UserDocumentType.DNI,
        UserDocumentType.CE,
        UserDocumentType.RUC,
        UserDocumentType.PASSPORT,
    ],
    Nationality.VE: [
        UserDocumentType.CI,
        UserDocumentType.RIF,
        UserDocumentType.PASSPORT,
    ],
}

NATIONALITY_NAMES: dict["Nationality", str] = {
    Nationality.CO: "Colombia",
    Nationality.MX: "México",
    Nationality.AR: "Argentina",
    Nationality.PE: "Perú",
    Nationality.VE: "Venezuela",
}

NATIONALITY_PHONE_PREFIX: dict["Nationality", str] = {
    Nationality.CO: "+57",
    Nationality.MX: "+52",
    Nationality.AR: "+54",
    Nationality.PE: "+51",
    Nationality.VE: "+58",
}
