"""Schemas de flujos IVR: alta, edición y respuesta."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import Field

from core.base.schema_base import BaseSchema


class IvrFlowCreateRequest(BaseSchema):
    name: str = Field(description="Nombre del flujo IVR")
    description: str | None = Field(default=None, description="Descripción del flujo")
    config: dict[str, Any] = Field(
        description=(
            "CampaignIvrConfig compilado (entry_node, defaults, nodes) "
            "listo para Helena"
        )
    )
    graph: dict[str, Any] | None = Field(
        default=None,
        description="Grafo crudo de React Flow para reeditar en el diseñador",
    )
    redial_config: dict[str, Any] | None = Field(
        default=None,
        description="Configuración de remarcado (maxAttempts, retryDelaySeconds)",
    )
    variables: dict[str, Any] | None = Field(
        default=None,
        description="Variables por defecto para Helena (AMD_*, PJSIP_TRUNK, …)",
    )
    outcomes: dict[str, Any] | None = Field(
        default=None,
        description="Etiquetas de resultado por desenlace: {nodo: {clave: etiqueta}}",
    )
    calls_per_second: int | None = Field(
        default=None,
        description="Ritmo de marcación (llamadas/seg); vacío usa el default de Helena",
    )
    max_concurrent: int | None = Field(
        default=None,
        description="Tope de llamadas simultáneas; vacío usa el default de Helena",
    )
    caller_id: str | None = Field(
        default=None, description="Caller ID por defecto para el bulk"
    )
    contact_policy_id: str | None = Field(
        default=None,
        description="ID de la política de contacto de Helena (horario de marcación)",
    )


class IvrFlowUpdateRequest(BaseSchema):
    name: str | None = Field(default=None, description="Nuevo nombre")
    description: str | None = Field(default=None, description="Nueva descripción")
    config: dict[str, Any] | None = Field(
        default=None, description="Nuevo CampaignIvrConfig"
    )
    graph: dict[str, Any] | None = Field(
        default=None, description="Nuevo grafo React Flow"
    )
    redial_config: dict[str, Any] | None = Field(
        default=None, description="Nueva configuración de remarcado"
    )
    variables: dict[str, Any] | None = Field(
        default=None, description="Nuevas variables por defecto para Helena"
    )
    outcomes: dict[str, Any] | None = Field(
        default=None, description="Nuevas etiquetas de resultado por desenlace"
    )
    calls_per_second: int | None = Field(
        default=None,
        description="Ritmo de marcación (llamadas/seg); vacío usa el default de Helena",
    )
    max_concurrent: int | None = Field(
        default=None,
        description="Tope de llamadas simultáneas; vacío usa el default de Helena",
    )
    caller_id: str | None = Field(
        default=None, description="Caller ID por defecto para el bulk"
    )
    contact_policy_id: str | None = Field(
        default=None,
        description="ID de la política de contacto de Helena (horario de marcación)",
    )


class IvrFlowResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID del flujo IVR")
    portfolio_id: uuid.UUID = Field(description="ID del portafolio dueño")
    name: str = Field(description="Nombre del flujo")
    description: str | None = Field(default=None, description="Descripción del flujo")
    config: dict[str, Any] = Field(description="CampaignIvrConfig compilado")
    graph: dict[str, Any] | None = Field(default=None, description="Grafo React Flow")
    redial_config: dict[str, Any] | None = Field(
        default=None, description="Configuración de remarcado"
    )
    variables: dict[str, Any] | None = Field(
        default=None, description="Variables por defecto para Helena"
    )
    outcomes: dict[str, Any] | None = Field(
        default=None, description="Etiquetas de resultado por desenlace"
    )
    calls_per_second: int | None = Field(
        default=None,
        description="Ritmo de marcación (llamadas/seg); vacío usa el default de Helena",
    )
    max_concurrent: int | None = Field(
        default=None,
        description="Tope de llamadas simultáneas; vacío usa el default de Helena",
    )
    caller_id: str | None = Field(
        default=None, description="Caller ID por defecto para el bulk"
    )
    contact_policy_id: str | None = Field(
        default=None,
        description="ID de la política de contacto de Helena (horario de marcación)",
    )
    created_at: datetime = Field(description="Fecha de creación")
    updated_at: datetime | None = Field(
        default=None, description="Fecha de última actualización"
    )
