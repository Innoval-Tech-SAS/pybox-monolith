"""Schemas del reporte de campaña IVR: desenlaces y desglose por nodo."""

from pydantic import Field

from core.base.schema_base import BaseSchema


class IvrOutcomeRow(BaseSchema):
    key: str = Field(description="Clave técnica del desenlace")
    label: str | None = Field(
        default=None, description="Etiqueta configurada en el diseñador; null si no hay"
    )
    count: int = Field(description="Llamadas con este resultado")
    percentage: float = Field(description="Porcentaje sobre el total tipificado")


class IvrBreakdownRow(BaseSchema):
    value: str | None = Field(
        default=None, description="Valor agrupado; null si no se reportó"
    )
    count: int = Field(description="Llamadas con ese valor")


class IvrFunnelSchema(BaseSchema):
    """Embudo de la campaña. Cada escalón es un subconjunto del anterior."""

    dialed: int = Field(default=0, description="Llamadas marcadas")
    answered: int = Field(default=0, description="Contestaron (dialStatus = ANSWER)")
    human: int = Field(default=0, description="El AMD detectó una persona")
    interacted: int = Field(
        default=0, description="Marcaron alguna tecla o capturaron datos"
    )
    transferred: int = Field(default=0, description="Llegaron a un agente")


class IvrDurationSchema(BaseSchema):
    total_seconds: int = Field(
        default=0, description="Segundos totales de conversación"
    )
    average_seconds: int = Field(default=0, description="Duración promedio por llamada")
    billable_seconds: int = Field(
        default=0, description="Segundos facturables reportados"
    )


class IvrCampaignReportSchema(BaseSchema):
    campaign_id: str = Field(description="Campaña reportada")
    total_calls: int = Field(default=0, description="Interacciones registradas")
    typified_calls: int = Field(
        default=0, description="Interacciones con un resultado resuelto"
    )
    outcomes: list[IvrOutcomeRow] = Field(
        default_factory=list, description="Distribución de resultados de negocio"
    )
    by_amd: list[IvrBreakdownRow] = Field(
        default_factory=list, description="Distribución por resultado del AMD"
    )
    by_end_node: list[IvrBreakdownRow] = Field(
        default_factory=list, description="Distribución por nodo final del flujo"
    )
    by_attempt: list[IvrBreakdownRow] = Field(
        default_factory=list, description="Distribución por número de intento"
    )
    funnel: IvrFunnelSchema = Field(description="Embudo de la campaña")
    duration: IvrDurationSchema = Field(description="Resumen de duraciones")
