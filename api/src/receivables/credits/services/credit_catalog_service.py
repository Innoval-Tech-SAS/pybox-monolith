"""Catálogo de tipos de crédito (valores fijos derivados del enum)."""

from receivables.credits.enums.credit_enums import CREDIT_TYPE_LABELS, CreditTypes
from receivables.credits.schemas.credit_catalog_schemas import CreditTypeOption


class CreditCatalogService:
    """Catálogos de valores fijos del módulo de créditos.

    No toca base de datos: se arma desde los enums, que son la fuente de verdad.
    Existe para que el front no declare su propia copia de la lista ni de sus etiquetas.
    """

    def list_credit_types(self) -> list[CreditTypeOption]:
        return [
            CreditTypeOption(
                value=credit_type.value, label=CREDIT_TYPE_LABELS[credit_type]
            )
            for credit_type in CreditTypes
        ]
