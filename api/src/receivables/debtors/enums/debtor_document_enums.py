"""Categoría de un documento colgado de un deudor."""

from enum import StrEnum


class DebtorDocumentCategory(StrEnum):
    """Para qué sirve un documento colgado de un deudor.

    Acotado al repositorio documental del titular. Reemplaza la porción "ámbito deudor"
    del viejo enum global `DocumentCategory`, que mezclaba las categorías de los cinco
    ámbitos en un solo tipo y permitía guardar, por ejemplo, un `FOTO_PERFIL` en un
    documento de deudor.
    """

    IDENTITY = "IDENTIDAD"
    PAYMENT_RECEIPT = "COMPROBANTE_PAGO"
    CONTRACT = "CONTRATO"
    OTHER = "OTRO"


# Nombre legible por categoría — fuente de verdad expuesta por API para los selects del
# front, que no mantiene copia propia.
DEBTOR_DOCUMENT_CATEGORY_LABELS: dict[DebtorDocumentCategory, str] = {
    DebtorDocumentCategory.IDENTITY: "Documento de identidad",
    DebtorDocumentCategory.PAYMENT_RECEIPT: "Comprobante de pago",
    DebtorDocumentCategory.CONTRACT: "Contrato",
    DebtorDocumentCategory.OTHER: "Otro",
}

# Categorías que el titular puede subir a su propio repositorio desde el portal SELF.
# Hoy son todas — el enum ya quedó acotado al ámbito deudor, así que no hay categoría de
# otro ámbito que pudiera colarse. Se mantiene como punto único de control por si más
# adelante aparece una categoría del deudor que solo pueda aportar la entidad.
SELF_UPLOADABLE_DEBTOR_CATEGORIES: frozenset[DebtorDocumentCategory] = frozenset(
    DebtorDocumentCategory
)
