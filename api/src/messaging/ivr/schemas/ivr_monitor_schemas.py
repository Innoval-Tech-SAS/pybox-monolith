"""Schemas del monitor IVR en vivo: llamadas y estadísticas de campaña."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import Field

from core.base.schema_base import BaseSchema
from messaging.ivr.enums.ivr_enums import IvrCallStatus
from messaging.ivr.models.ivr_interaction_model import IvrInteractionModel


class IvrCallSchema(BaseSchema):
    """Una llamada tal como la consume el monitor.

    Equivalente a `NormalizedCall` de iris
    (`call-monitor/interfaces/call-monitor.interfaces.ts`).
    """

    interaction_id: str = Field(description="ID de la interacción en Helena")
    bulk_id: str = Field(description="ID del bulk (ejecución) en Helena")
    campaign_id: uuid.UUID | None = Field(default=None, description="Campaña de Pybox")
    phone: str = Field(description="Número marcado")
    customer_name: str | None = Field(default=None, description="Nombre del cliente")
    customer_document: str | None = Field(
        default=None, description="Documento del cliente"
    )
    status: IvrCallStatus = Field(description="Estado visual derivado de la llamada")
    last_event: str | None = Field(
        default=None, description="Último evento recibido de Helena"
    )
    attempt_number: int = Field(
        description="Número de intento de remarcación (1 = original)"
    )

    amd_status: str | None = Field(default=None, description="Resultado del AMD")
    amd_cause: str | None = Field(
        default=None, description="Causa reportada por el AMD"
    )
    dial_status: str | None = Field(
        default=None, description="Resultado de la marcación"
    )
    transferred: bool = Field(
        default=False, description="Si la llamada llegó a un agente"
    )

    last_digit: str | None = Field(
        default=None, description="Última tecla marcada por el cliente"
    )
    ivr_end_node_id: str | None = Field(
        default=None, description="Nodo del flujo donde terminó la llamada"
    )
    ivr_end_reason: str | None = Field(
        default=None, description="Motivo de cierre del IVR"
    )
    outcome_key: str | None = Field(
        default=None, description="Clave del resultado de negocio"
    )
    outcome_label: str | None = Field(
        default=None, description="Etiqueta del resultado configurada en el diseñador"
    )
    dtmf_events: list[Any] | None = Field(
        default=None, description="Teclas marcadas, en orden"
    )
    collected_data: list[Any] | None = Field(
        default=None, description="Datos capturados por los nodos collect"
    )

    duration_seconds: int | None = Field(
        default=None, description="Duración total en segundos"
    )
    started_at: datetime | None = Field(
        default=None, description="Inicio de la marcación"
    )
    answered_at: datetime | None = Field(
        default=None, description="Momento en que contestaron"
    )
    transfer_started_at: datetime | None = Field(
        default=None, description="Inicio de la transferencia"
    )
    ended_at: datetime | None = Field(default=None, description="Fin de la llamada")
    updated_at: datetime | None = Field(
        default=None, description="Última actualización"
    )

    @classmethod
    def from_model(cls, row: IvrInteractionModel) -> "IvrCallSchema":
        return cls(
            interaction_id=row.interaction_id,
            bulk_id=row.bulk_id,
            campaign_id=row.campaign_id,
            phone=row.phone,
            customer_name=row.customer_name,
            customer_document=row.customer_document,
            status=row.status,
            last_event=row.last_event,
            attempt_number=row.attempt_number or 1,
            amd_status=row.amd_status,
            amd_cause=row.amd_cause,
            dial_status=row.dial_status,
            transferred=bool(row.transferred),
            last_digit=_last_digit(row.dtmf_events),
            ivr_end_node_id=row.ivr_end_node_id,
            ivr_end_reason=row.ivr_end_reason,
            outcome_key=row.outcome_key,
            outcome_label=row.outcome_label,
            dtmf_events=row.dtmf_events,
            collected_data=row.collected_data,
            duration_seconds=row.duration_seconds,
            started_at=row.started_at,
            answered_at=row.answered_at,
            transfer_started_at=row.transfer_started_at,
            ended_at=row.ended_at,
            updated_at=row.updated_at,
        )


def _last_digit(dtmf_events: list[Any] | None) -> str | None:
    if not dtmf_events:
        return None
    last = dtmf_events[-1]
    if not isinstance(last, dict):
        return None
    digit = last.get("digit")
    return str(digit) if digit not in (None, "", "NO_INPUT") else None


class IvrCampaignStatsSchema(BaseSchema):
    """Contadores de una campaña IVR.

    Los contadores de AMD, pulsaciones y transferencias son **acumulados**, no
    derivados del estado actual: una llamada detectada como humana que después
    entra al IVR y termina sigue contando como humana. Por eso se calculan sobre
    los campos persistidos (`amd_status`, `dtmf_events`, `transferred`) y no
    sobre `status`.
    """

    total_calls: int = Field(default=0, description="Llamadas totales del bulk")
    active_calls: int = Field(default=0, description="Llamadas aún en curso")
    human_detections: int = Field(default=0, description="AMD detectó persona")
    machine_detections: int = Field(
        default=0, description="AMD detectó máquina o dudoso"
    )
    menu_selections: int = Field(
        default=0, description="Llamadas con al menos una tecla marcada"
    )
    transfers: int = Field(default=0, description="Llamadas transferidas a un agente")
    completed: int = Field(default=0, description="Llamadas completadas")
    failed: int = Field(default=0, description="Llamadas fallidas")
    no_answer: int = Field(default=0, description="Llamadas sin respuesta")
    cancelled: int = Field(default=0, description="Llamadas canceladas")


class IvrSnapshotSchema(BaseSchema):
    """Estado inicial del monitor: lo que el stream no puede entregar por sí solo."""

    active_calls: list[IvrCallSchema] = Field(
        default_factory=list,
        description="Llamadas en curso y las que acaban de terminar",
    )
    stats: IvrCampaignStatsSchema = Field(description="Contadores de la campaña")
    generated_at: datetime = Field(description="Momento en que se generó el snapshot")


class IvrCallListResponse(BaseSchema):
    items: list[IvrCallSchema] = Field(default_factory=list)
    total: int = Field(default=0)
    page: int = Field(default=1)
    page_size: int = Field(default=50)
