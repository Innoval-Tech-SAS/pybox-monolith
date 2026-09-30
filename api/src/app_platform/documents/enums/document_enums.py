"""Constantes transversales del almacén de documentos.

Acá solo vive lo que es cierto para CUALQUIER documento, sin importar de qué cuelga:
límite de tamaño y tipos aceptados. El "para qué sirve" (la categoría) ya no es un
enum único global — cada dominio declara el suyo, acotado a sus propios casos:

- `receivables/debtors/enums/debtor_document_enums.py` → `DebtorDocumentCategory`
- `app_platform/support/enums/support_enums.py` → `TicketDocumentCategory`
- `receivables/portfolios/enums/portfolio_document_enums.py` →
  `PortfolioDocumentCategory`

Los casos 1:1 (documento fiscal/mercantil/representante de una entidad, foto de perfil
de un usuario, extracto, notificación judicial, ejecución de reporte) no necesitan
categoría: la columna que apunta al documento ya dice qué es.
"""

# Tipos de los artefactos que genera la API. Van aparte de ALLOWED_DOCUMENT_TYPES a
# propósito: esa lista acota lo que un usuario puede empujar al almacén, y estos no
# vienen de un usuario sino de código nuestro.
CSV_CONTENT_TYPE = "text/csv"
XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# Tipos aceptados: extensión → content-type canónico.
#
# Se valida el par extensión↔content-type declarado, no solo la extensión: así renombrar
# un ejecutable a .pdf no alcanza para que entre.
ALLOWED_DOCUMENT_TYPES: dict[str, str] = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}

MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
