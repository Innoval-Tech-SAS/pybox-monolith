"""Schemas de extractos: solicitud de generación y respuesta."""

import uuid
from datetime import datetime

from pydantic import Field

from core.base.schema_base import BaseSchema


class GenerateStatementRequest(BaseSchema):
    """Qué extracto generar. Sin `credit_id`: consolidado con todos los créditos
    activos del deudor en el portafolio. Con `credit_id`: solo ese crédito."""

    credit_id: uuid.UUID | None = Field(
        default=None, description="Crédito puntual, o vacío para consolidado"
    )


class StatementResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID del extracto")
    debtor_id: uuid.UUID = Field(description="ID del deudor")
    portfolio_id: uuid.UUID = Field(description="ID del portafolio")
    organization_id: uuid.UUID = Field(description="ID de la organización acreedora")
    organization_name: str = Field(description="Nombre de la organización acreedora")
    credit_id: uuid.UUID | None = Field(
        default=None, description="Crédito puntual, o vacío si es consolidado"
    )
    credit_number: str | None = Field(
        default=None, description="Número de crédito, si es puntual"
    )
    cutoff_date: datetime = Field(description="Fecha de corte del extracto")
    document_id: uuid.UUID = Field(description="ID del documento (PDF) generado")
    created_at: datetime = Field(description="Fecha de generación")


class StatementListResponse(BaseSchema):
    items: list[StatementResponse] = Field(
        description="Extractos, del más reciente al más antiguo"
    )
    total: int = Field(description="Cantidad de extractos")
