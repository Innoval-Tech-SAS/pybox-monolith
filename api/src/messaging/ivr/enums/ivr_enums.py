from enum import StrEnum


class IvrCallStatus(StrEnum):
    """Estado visual de una interacción (llamada) de Helena.

    Derivado de los campos de la interacción en cada evento, no reportado
    directamente por Helena. Portado del modelo de `iris`
    (`call-monitor-projection.service.ts:deriveStatus`).
    """

    QUEUED = "QUEUED"
    RINGING = "RINGING"
    HUMAN_DETECTED = "HUMAN_DETECTED"
    MACHINE_DETECTED = "MACHINE_DETECTED"
    IN_IVR = "IN_IVR"
    TRANSFERRING = "TRANSFERRING"
    COMPLETED = "COMPLETED"
    NO_ANSWER = "NO_ANSWER"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


TERMINAL_CALL_STATUSES: frozenset[IvrCallStatus] = frozenset(
    {
        IvrCallStatus.COMPLETED,
        IvrCallStatus.NO_ANSWER,
        IvrCallStatus.FAILED,
        IvrCallStatus.CANCELLED,
    }
)


class HelenaEvent(StrEnum):
    """Eventos que Helena despacha por webhook.

    Catálogo verificado contra `helena-collectia`:
    `apps/helena-reporting/src/features/events/interaction-events.service.ts`
    y `apps/helena-reporting/src/features/campaigns/campaigns.service.ts`.
    """

    # Interacción (traen `interaction` en el cuerpo)
    INTERACTION_STARTED = "INTERACTION_STARTED"
    AMD_RESULT = "AMD_RESULT"
    IVR_MENU_SELECTED = "IVR_MENU_SELECTED"
    IVR_COLLECT_COMPLETE = "IVR_COLLECT_COMPLETE"
    IVR_TRANSFER_INITIATED = "IVR_TRANSFER_INITIATED"
    IVR_TRANSFER_ANSWERED = "IVR_TRANSFER_ANSWERED"
    IVR_TRANSFER_ENDED = "IVR_TRANSFER_ENDED"
    IVR_TRANSFER_NO_ANSWER = "IVR_TRANSFER_NO_ANSWER"
    IVR_COMPLETED = "IVR_COMPLETED"
    CALL_ENDED = "CALL_ENDED"
    ORIGINATE_FAILED = "ORIGINATE_FAILED"
    INTERACTION_CANCELLED = "INTERACTION_CANCELLED"
    INTERACTION_TECHNICAL_TIMEOUT = "INTERACTION_TECHNICAL_TIMEOUT"
    INTERACTION_OUT_OF_SCHEDULE = "INTERACTION_OUT_OF_SCHEDULE"

    # Ciclo de vida de la campaña (payload plano, sin `interaction`)
    CAMPAIGN_PENDING = "CAMPAIGN_PENDING"
    CAMPAIGN_PAUSED = "CAMPAIGN_PAUSED"
    CAMPAIGN_RESUMED = "CAMPAIGN_RESUMED"
    CAMPAIGN_CANCELLED = "CAMPAIGN_CANCELLED"
    CAMPAIGN_FINISHED = "CAMPAIGN_FINISHED"

    # Prueba manual disparada desde `POST /reporting/webhooks/:id/test`
    TEST_EVENT = "TEST_EVENT"


#: Eventos que cierran definitivamente una interacción.
#:
#: `INTERACTION_OUT_OF_SCHEDULE` entra aquí porque en Helena es terminal: la
#: llamada se descarta por la política de contacto y **no se reintenta en la
#: siguiente ventana** (`interactions.repository.ts:bulkMarkOutOfSchedule`).
#: Como nunca se marca, tampoco llega después un `CALL_ENDED` que la cierre.
TERMINAL_EVENTS: frozenset[str] = frozenset(
    {
        HelenaEvent.CALL_ENDED,
        HelenaEvent.ORIGINATE_FAILED,
        HelenaEvent.INTERACTION_CANCELLED,
        HelenaEvent.INTERACTION_TECHNICAL_TIMEOUT,
        HelenaEvent.INTERACTION_OUT_OF_SCHEDULE,
    }
)

#: Eventos que cierran la llamada sin haberla llegado a marcar. Helena los
#: aplica solo sobre interacciones con `startedAt`/`endedAt` nulos, así que no
#: pueden pisar el resultado de una llamada que sí se cursó.
CANCELLING_EVENTS: frozenset[str] = frozenset(
    {
        HelenaEvent.INTERACTION_CANCELLED,
        HelenaEvent.INTERACTION_OUT_OF_SCHEDULE,
    }
)


class IvrExecutionStatus(StrEnum):
    """Estado de un bulk despachado a Helena (`ejecuciones_ivr`).

    Refleja el estado del `status` que Helena reporta en los eventos
    `CAMPAIGN_*` (ver `HELENA_STATUS_TO_EXECUTION_STATUS`). No hay un evento
    explícito de "arrancó a marcar": se asume `RUNNING` desde el despacho
    porque el bulk se manda sin `scheduledDate/Time` (procesamiento inmediato).
    """

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"
    FINISHED = "FINISHED"


#: Estados terminales: no aceptan más pausar/reanudar/cancelar.
TERMINAL_EXECUTION_STATUSES: frozenset[IvrExecutionStatus] = frozenset(
    {IvrExecutionStatus.CANCELLED, IvrExecutionStatus.FINISHED}
)

#: `status` (minúsculas) que trae el payload de los eventos CAMPAIGN_* de Helena.
HELENA_STATUS_TO_EXECUTION_STATUS: dict[str, IvrExecutionStatus] = {
    "pending": IvrExecutionStatus.PENDING,
    "running": IvrExecutionStatus.RUNNING,
    "paused": IvrExecutionStatus.PAUSED,
    "cancelled": IvrExecutionStatus.CANCELLED,
    "finished": IvrExecutionStatus.FINISHED,
}


#: Eventos que se registran en Helena al arrancar la API. Se registra la lista
#: explícita en lugar de `["*"]` para no recibir eventos que no procesamos.
SUBSCRIBED_EVENTS: tuple[str, ...] = (
    HelenaEvent.INTERACTION_STARTED,
    HelenaEvent.AMD_RESULT,
    HelenaEvent.IVR_MENU_SELECTED,
    HelenaEvent.IVR_COLLECT_COMPLETE,
    HelenaEvent.IVR_TRANSFER_INITIATED,
    HelenaEvent.IVR_TRANSFER_ANSWERED,
    HelenaEvent.IVR_TRANSFER_ENDED,
    HelenaEvent.IVR_TRANSFER_NO_ANSWER,
    HelenaEvent.IVR_COMPLETED,
    HelenaEvent.CALL_ENDED,
    HelenaEvent.ORIGINATE_FAILED,
    HelenaEvent.INTERACTION_CANCELLED,
    HelenaEvent.INTERACTION_TECHNICAL_TIMEOUT,
    HelenaEvent.INTERACTION_OUT_OF_SCHEDULE,
    HelenaEvent.CAMPAIGN_PENDING,
    HelenaEvent.CAMPAIGN_PAUSED,
    HelenaEvent.CAMPAIGN_RESUMED,
    HelenaEvent.CAMPAIGN_CANCELLED,
    HelenaEvent.CAMPAIGN_FINISHED,
)
