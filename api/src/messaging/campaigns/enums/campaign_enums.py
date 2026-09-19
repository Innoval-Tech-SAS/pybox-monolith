from enum import StrEnum


class CampaignStatus(StrEnum):
    DRAFT = "BORRADOR"
    SCHEDULED = "PROGRAMADA"
    RUNNING = "EN_EJECUCION"
    COMPLETED = "COMPLETADA"
    FAILED = "FALLIDA"
    PAUSED = "PAUSADA"
    CANCELLED = "CANCELADA"


class Periodicity(StrEnum):
    ONCE = "UNA_VEZ"
    IMMEDIATE = "INMEDIATO"
    DAILY = "DIARIO"
    WEEKLY = "SEMANAL"
    MONTHLY = "MENSUAL"


# Sin uso detectado en el resto del backend (repository/service/controller) al momento
# de esta normalización -- se deja el valor consistente por si se retoma, no se borra
# la clase sin confirmar con el equipo.
class DeliveryStatus(StrEnum):
    PENDING = "PENDIENTE"  # En cola, no enviado aún
    QUEUED = "EN_COLA"  # Enviado a Sent, esperando respuesta
    SENT = "ENVIADO"  # Sent confirmó recepción
    DELIVERED = "ENTREGADO"  # Usuario recibió (callback de Sent)
    READ = "LEIDO"  # Usuario abrió (callback de Sent)
    FAILED = "FALLIDO"  # Error definitivo
    BOUNCED = "REBOTADO"  # Número inválido
