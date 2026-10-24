"""Schemas de ejecución IVR: estado, asignación de flujo y control de campaña."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import Field

from core.base.schema_base import BaseSchema
from messaging.ivr.enums.ivr_enums import IvrExecutionStatus
from messaging.ivr.models.ivr_execution_model import IvrExecutionModel


class IvrExecutionSchema(BaseSchema):
    bulk_id: str = Field(description="ID del bulk en Helena")
    campaign_id: uuid.UUID = Field(description="Campaña que lo despachó")
    campaign_time_id: uuid.UUID | None = Field(
        default=None, description="Programación que disparó este envío"
    )
    status: IvrExecutionStatus = Field(description="Estado local del bulk")
    quantity: int = Field(description="Cantidad de destinatarios del bulk")
    calls_per_second: int | None = Field(
        default=None, description="Ritmo con el que se despachó"
    )
    max_concurrent: int | None = Field(
        default=None, description="Tope de simultáneas con el que se despachó"
    )
    dispatched_at: datetime = Field(description="Momento del despacho a Helena")
    finished_at: datetime | None = Field(
        default=None, description="Momento en que cerró"
    )

    @classmethod
    def from_model(cls, row: IvrExecutionModel) -> "IvrExecutionSchema":
        return cls(
            bulk_id=row.bulk_id,
            campaign_id=row.campaign_id,
            campaign_time_id=row.campaign_time_id,
            status=row.status,
            quantity=row.quantity,
            calls_per_second=row.calls_per_second,
            max_concurrent=row.max_concurrent,
            dispatched_at=row.dispatched_at,
            finished_at=row.finished_at,
        )


class IvrExecutionStatusResponse(BaseSchema):
    """Estado combinado: la fila local (fuente rápida) + el snapshot en
    vivo de Helena."""

    execution: IvrExecutionSchema = Field(description="Estado registrado en Punvox")
    helena: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Respuesta cruda de Helena (GET /calls/queue/status); null "
            "si la consulta falló"
        ),
    )


class IvrAllocationRequest(BaseSchema):
    calls_per_second: int | None = Field(
        default=None, ge=1, description="Nuevo ritmo de marcación (llamadas/seg)"
    )
    max_concurrent: int | None = Field(
        default=None, ge=1, description="Nuevo tope de llamadas simultáneas"
    )
