from enum import StrEnum


class SupportCaseType(StrEnum):
    INCIDENT = "INCIDENTE"
    REQUIREMENT = "REQUERIMIENTO"


class SupportTicketStatus(StrEnum):
    NEW = "NUEVO"
    OPEN = "ABIERTO"
    IN_PROGRESS = "EN_PROGRESO"
    PENDING_CLIENT = "PENDIENTE_CLIENTE"
    PENDING_THIRD = "PENDIENTE_TERCERO"
    RESOLVED = "RESUELTO"
    CLOSED = "CERRADO"


class SupportTicketPriority(StrEnum):
    LOW = "BAJA"
    MEDIUM = "MEDIA"
    HIGH = "ALTA"
    URGENT = "URGENTE"


# Valores de SupportTicketModel.system_topic (columna `tema_sistema`, String libre —
# no es un Enum de DB, agregar un topic nuevo no requiere migración de tipo). Es el
# tema real de CUALQUIER ticket (creado a mano o por el sistema), más granular que
# case_type. case_type se deriva de a cuál de estos dos enums pertenece el topic:
# ver `_TOPIC_CASE_TYPE` en support_schemas.py.
class RequirementTopic(StrEnum):
    NEW_FEATURE = "NUEVA_FUNCIONALIDAD"
    DOCUMENT_VALIDATION = "VALIDACION_DOCUMENTO"
    WHATSAPP_NUMBER_REQUEST = "SOLICITUD_NUMERO_WHATSAPP"


class IncidentTopic(StrEnum):
    BUG_REPORT = "REPORTE_ERROR"
    ACCESS_ISSUE = "PROBLEMA_ACCESO"
    GENERAL_INQUIRY = "CONSULTA_GENERAL"
    OTHER = "OTRO"


# Topics de autogestión del titular (rol USER, scope SELF) iniciados desde el
# calendario financiero. Solo visibles/creables por usuarios SELF y solo resolubles
# por el CUSTOMER_SERVICE de la organización dueña del crédito. Cada uno dispara un
# efecto secundario sobre el pago al resolverse (ver resolve_ticket).
class PaymentTopic(StrEnum):
    PAYMENT_RESCHEDULE = "REPROGRAMACION_PAGO"
    PAYMENT_VALIDATION = "VALIDACION_PAGO"
    # El titular pide dar de baja (saldar) todo un crédito adjuntando comprobante; al
    # aprobar se registra un pago por el monto total y el crédito se desactiva.
    CREDIT_SETTLEMENT = "BAJA_CREDITO"


# Para qué sirve un documento colgado de un ticket (tabla `documentos_ticket`).
# Reemplaza la porción "ámbito ticket" del viejo enum global `DocumentCategory`:
# acotado a los dos casos reales del módulo, no a los quince de todos los ámbitos
# juntos.
class TicketDocumentCategory(StrEnum):
    TICKET_ATTACHMENT = "ADJUNTO_TICKET"
    TICKET_CLOSURE = "EVIDENCIA_CIERRE"


# Igual que PaymentTopic: topic de autogestión, pero del titular consigo mismo, no con
# un crédito de una organización — por eso el ticket se crea sin organization_id
# (prefer_global=True en _auto_assign) y lo resuelve cualquier Atención al Cliente
# GLOBAL, no la de una organización puntual. Ver
# OnboardingService.submit_identity_document y SupportService.resolve_ticket.
class IdentityTopic(StrEnum):
    IDENTITY_VALIDATION = "VALIDACION_IDENTIDAD"


TICKET_DOCUMENT_CATEGORY_LABELS: dict[TicketDocumentCategory, str] = {
    TicketDocumentCategory.TICKET_ATTACHMENT: "Adjunto de ticket",
    TicketDocumentCategory.TICKET_CLOSURE: "Evidencia de cierre",
}


class SupportTicketEventType(StrEnum):
    CREATED = "CREADO"
    STATUS_CHANGED = "CAMBIO_ESTADO"
    PRIORITY_CHANGED = "CAMBIO_PRIORIDAD"
    ASSIGNED = "ASIGNADO"
    REASSIGNED = "REASIGNADO"
    ESCALATED = "ESCALADO"
    RESOLVED = "RESUELTO"
    CLOSED = "CERRADO"
    REOPENED = "REABIERTO"
