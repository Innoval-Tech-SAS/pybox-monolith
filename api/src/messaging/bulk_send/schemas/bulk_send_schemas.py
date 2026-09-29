"""Schema de respuesta del envío masivo: totales de éxito, fallo y omitidos."""

from pydantic import Field

from core.base.schema_base import BaseSchema


class BulkSendResponse(BaseSchema):
    total_sent: int = Field(description="Total de filas procesadas")
    success_count: int = Field(description="Envíos exitosos")
    failure_count: int = Field(description="Envíos fallidos")
    unique_customers: int = Field(description="Destinatarios únicos")
    skipped_rows: int = Field(description="Filas omitidas por datos inválidos")
    pending_approval_count: int = Field(
        default=0,
        description=(
            "Filas de WhatsApp omitidas porque el teléfono espera aprobación "
            "del canal (solicitud de consentimiento)"
        ),
    )
