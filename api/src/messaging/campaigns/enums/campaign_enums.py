from enum import Enum


class CampaignStatus(str, Enum):
    DRAFT = "borrador"
    SCHEDULED = "programada"
    RUNNING = "en ejecución"
    COMPLETED = "completada"
    FAILED = "fallida"
    PAUSED = "pausada"
    CANCELLED = "cancelada"


class Periodicity(str, Enum):
    ONCE = "once"
    IMMEDIATE = "immediate"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class DeliveryStatus(str, Enum):
    PENDING = "pendiente"  # En cola, no enviado aún
    QUEUED = "en cola"  # Enviado a Sent, esperando respuesta
    SENT = "enviado"  # Sent confirmó recepción
    DELIVERED = "entregado"  # Usuario recibió (callback de Sent)
    READ = "leído"  # Usuario abrió (callback de Sent)
    FAILED = "fallido"  # Error definitivo
    BOUNCED = "rebotado"  # Número inválido
