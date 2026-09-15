from enum import StrEnum


class PortfolioDocumentCategory(StrEnum):
    """Para qué sirve un documento colgado de un portafolio (tabla
    `documentos_portafolio`).

    Los dos son artefactos que genera la propia API, no subidas libres de usuario: el
    CSV de una exportación de segmento y el archivo fuente de una carga de portafolio o
    de plan de cuotas ya parseada, que se archiva como evidencia.
    """

    SEGMENT_EXPORT = "EXPORTACION_SEGMENTO"
    PORTFOLIO_SOURCE = "ARCHIVO_PORTAFOLIO"


PORTFOLIO_DOCUMENT_CATEGORY_LABELS: dict[PortfolioDocumentCategory, str] = {
    PortfolioDocumentCategory.SEGMENT_EXPORT: "Exportación de segmento",
    PortfolioDocumentCategory.PORTFOLIO_SOURCE: "Archivo de portafolio",
}
