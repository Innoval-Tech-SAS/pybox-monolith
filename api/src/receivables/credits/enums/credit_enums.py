"""Tipo de crédito desde la perspectiva del titular (qué se debe)."""

from enum import StrEnum


class CreditTypes(StrEnum):
    """Qué se debe, desde la perspectiva del titular.

    Es el eje que el titular ve en su home (rol USER, scope SELF): determina el
    color del evento en el calendario y el ícono en el detalle de obligaciones.

    Antes este enum listaba sectores (Fintech, Retail, Moda…), que son un atributo
    de la entidad acreedora y no del crédito: se repetían idénticos en todos los
    créditos de una misma entidad. Eso vive ahora en `entidades.sector`
    (`EntitySectors`, en `identity.organizations.enums`). Un crédito de vehículo
    puede venir tanto de una entidad financiera como de una fintech.
    """

    CREDIT_CARD = "TARJETA_CREDITO"
    VEHICLE_CREDIT = "CREDITO_VEHICULO"
    CONSUMER_CREDIT = "CREDITO_CONSUMO"
    SCHOOL_TUITION = "COLEGIO_PENSION"
    ADMINISTRATION = "ADMINISTRACION"
    OTHER_SERVICE = "OTRO_SERVICIO"


# Nombre legible por código de tipo de crédito — fuente de verdad que se expone por
# API (GET /credits/types) para alimentar los selects y etiquetas del front, que no
# mantiene su propia copia. Mismo criterio que `ENTITY_SECTOR_LABELS` y
# `DOCUMENT_TYPE_LABELS`.
CREDIT_TYPE_LABELS: dict[str, str] = {
    CreditTypes.CREDIT_CARD: "Tarjeta de crédito",
    CreditTypes.VEHICLE_CREDIT: "Crédito de vehículo",
    CreditTypes.CONSUMER_CREDIT: "Crédito de consumo",
    CreditTypes.SCHOOL_TUITION: "Colegio / Pensión",
    CreditTypes.ADMINISTRATION: "Administración",
    CreditTypes.OTHER_SERVICE: "Otro / Servicio",
}

# Sinónimos aceptados en la columna "Tipo de producto" del CSV de portafolio, que
# viene escrito a mano por cada entidad. Se compara en mayúsculas, con y sin tilde;
# el código propio del enum también se acepta. Lo que no matchee cae en OTHER_SERVICE.
CREDIT_TYPE_ALIASES: dict[str, CreditTypes] = {
    **{credit_type.value.upper(): credit_type for credit_type in CreditTypes},
    "TC": CreditTypes.CREDIT_CARD,
    "TARJETA DE CREDITO": CreditTypes.CREDIT_CARD,
    "TARJETA DE CRÉDITO": CreditTypes.CREDIT_CARD,
    "CREDITO DE VEHICULO": CreditTypes.VEHICLE_CREDIT,
    "CRÉDITO DE VEHÍCULO": CreditTypes.VEHICLE_CREDIT,
    "VEHICULO": CreditTypes.VEHICLE_CREDIT,
    "VEHÍCULO": CreditTypes.VEHICLE_CREDIT,
    "CREDITO DE CONSUMO": CreditTypes.CONSUMER_CREDIT,
    "CRÉDITO DE CONSUMO": CreditTypes.CONSUMER_CREDIT,
    "CONSUMO": CreditTypes.CONSUMER_CREDIT,
    "COLEGIO / PENSION": CreditTypes.SCHOOL_TUITION,
    "COLEGIO / PENSIÓN": CreditTypes.SCHOOL_TUITION,
    "COLEGIO": CreditTypes.SCHOOL_TUITION,
    "PENSION": CreditTypes.SCHOOL_TUITION,
    "PENSIÓN": CreditTypes.SCHOOL_TUITION,
    "ADMINISTRACION": CreditTypes.ADMINISTRATION,
    "ADMINISTRACIÓN": CreditTypes.ADMINISTRATION,
    "OTRO / SERVICIO": CreditTypes.OTHER_SERVICE,
    "SERVICIO": CreditTypes.OTHER_SERVICE,
    "SERVICIOS": CreditTypes.OTHER_SERVICE,
    "OTRO": CreditTypes.OTHER_SERVICE,
    "OTROS": CreditTypes.OTHER_SERVICE,
}
