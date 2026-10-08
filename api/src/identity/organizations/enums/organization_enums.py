"""Estado de verificación y sector de una organización."""

from enum import StrEnum


class VerificationStatus(StrEnum):
    PENDING = "PENDIENTE"
    APPROVED = "APROBADO"
    DENIED = "DENEGADO"


class EntitySectors(StrEnum):
    """Sector al que pertenece la entidad acreedora. Se usa para segmentar cartera.

    Vivía en `creditos.tipo_credito` (enum `CreditTypes`), donde se repetía idéntico
    en cada crédito de una misma entidad. Es un atributo de la entidad, no del crédito:
    lo que sí varía crédito a crédito es qué se debe, y eso quedó en `CreditTypes`.
    """

    FINANCIAL_ENTITY = "ENTIDAD_FINANCIERA"
    FINTECH = "FINTECH"
    SERVICES = "SERVICIOS"
    PRODUCTS = "PRODUCTOS"
    FASHION = "MODA"
    RETAIL = "RETAIL"
    PYMES = "PYMES"
    OTHERS = "OTROS"


# Nombre legible por código de sector — fuente de verdad que se expone por API para
# alimentar los selects del front, que no debe mantener su propia copia. Mismo criterio
# que `DOCUMENT_TYPE_LABELS` en `app_platform.countries.enums`.
ENTITY_SECTOR_LABELS: dict[str, str] = {
    EntitySectors.FINANCIAL_ENTITY: "Entidad financiera",
    EntitySectors.FINTECH: "Fintech",
    EntitySectors.SERVICES: "Servicios",
    EntitySectors.PRODUCTS: "Productos",
    EntitySectors.FASHION: "Moda",
    EntitySectors.RETAIL: "Retail",
    EntitySectors.PYMES: "Pymes",
    EntitySectors.OTHERS: "Otros",
}
