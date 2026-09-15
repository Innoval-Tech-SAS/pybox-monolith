from enum import StrEnum


class JudicialPriority(StrEnum):
    """Urgencia de una notificación judicial, tal como la ordena el buzón del titular."""

    URGENT = "URGENTE"
    MEDIUM = "MEDIA"
    LOW = "BAJA"
    INFORMATIVE = "INFORMATIVA"


# Nombre legible por código de prioridad — fuente de verdad expuesta por API
# (GET /judicial-notifications/priorities) para el select del panel de la entidad y
# el chip del buzón. El front no mantiene su propia copia.
JUDICIAL_PRIORITY_LABELS: dict[str, str] = {
    JudicialPriority.URGENT: "Urgente",
    JudicialPriority.MEDIUM: "Media",
    JudicialPriority.LOW: "Baja",
    JudicialPriority.INFORMATIVE: "Informativa",
}
