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
    PASSPORT = "PASAPORTE"


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

NATIONALITY_TIMEZONE: dict["Nationality", str] = {
    Nationality.CO: "America/Bogota",
    Nationality.MX: "America/Mexico_City",
    Nationality.AR: "America/Argentina/Buenos_Aires",
    Nationality.PE: "America/Lima",
    Nationality.VE: "America/Caracas",
}

NATIONALITY_CURRENCY_CODE: dict["Nationality", str] = {
    Nationality.CO: "COP",
    Nationality.MX: "MXN",
    Nationality.AR: "ARS",
    Nationality.PE: "PEN",
    Nationality.VE: "VES",
}


class OrgFiscalDocumentType(str, Enum):
    NIT = "NIT"  # Colombia
    RFC = "RFC"  # México
    CUIT = "CUIT"  # Argentina
    RUC = "RUC"  # Perú
    RIF = "RIF"  # Venezuela


class OrgMercantileDocumentType(str, Enum):
    CAMARA_COMERCIO = "CAMARA_COMERCIO"  # Colombia
    REGISTRO_PUBLICO_COMERCIO = "REGISTRO_PUBLICO_COMERCIO"  # México
    INSCRIPCION_IGJ = "INSCRIPCION_IGJ"  # Argentina
    PARTIDA_SUNARP = "PARTIDA_SUNARP"  # Perú
    REGISTRO_MERCANTIL = "REGISTRO_MERCANTIL"  # Venezuela


ORG_FISCAL_DOCUMENT_BY_NATIONALITY: dict["Nationality", "OrgFiscalDocumentType"] = {
    Nationality.CO: OrgFiscalDocumentType.NIT,
    Nationality.MX: OrgFiscalDocumentType.RFC,
    Nationality.AR: OrgFiscalDocumentType.CUIT,
    Nationality.PE: OrgFiscalDocumentType.RUC,
    Nationality.VE: OrgFiscalDocumentType.RIF,
}

ORG_MERCANTILE_DOCUMENT_BY_NATIONALITY: dict[
    "Nationality", "OrgMercantileDocumentType"
] = {
    Nationality.CO: OrgMercantileDocumentType.CAMARA_COMERCIO,
    Nationality.MX: OrgMercantileDocumentType.REGISTRO_PUBLICO_COMERCIO,
    Nationality.AR: OrgMercantileDocumentType.INSCRIPCION_IGJ,
    Nationality.PE: OrgMercantileDocumentType.PARTIDA_SUNARP,
    Nationality.VE: OrgMercantileDocumentType.REGISTRO_MERCANTIL,
}

ORG_FISCAL_DOCUMENT_NAMES: dict["OrgFiscalDocumentType", str] = {
    OrgFiscalDocumentType.NIT: "NIT – Número de Identificación Tributaria",
    OrgFiscalDocumentType.RFC: "RFC – Registro Federal de Contribuyentes",
    OrgFiscalDocumentType.CUIT: "CUIT – Código Único de Identificación Tributaria",
    OrgFiscalDocumentType.RUC: "RUC – Registro Único de Contribuyentes",
    OrgFiscalDocumentType.RIF: "RIF – Registro de Información Fiscal",
}

ORG_MERCANTILE_DOCUMENT_NAMES: dict["OrgMercantileDocumentType", str] = {
    OrgMercantileDocumentType.CAMARA_COMERCIO: "Cámara de Comercio",
    OrgMercantileDocumentType.REGISTRO_PUBLICO_COMERCIO: "Registro Público de Comercio",
    OrgMercantileDocumentType.INSCRIPCION_IGJ: "Inscripción en el IGJ",
    OrgMercantileDocumentType.PARTIDA_SUNARP: "Partida Registral SUNARP",
    OrgMercantileDocumentType.REGISTRO_MERCANTIL: "Registro Mercantil",
}
