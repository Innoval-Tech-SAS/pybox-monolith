import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import Field

from core.base.schema_base import BaseSchema


class TrashedDocumentDomain(StrEnum):
    """Dominio dueño de un documento dado de baja.

    Es el discriminador de la papelera de Admin Global, no una columna de base de datos:
    cada valor identifica la tabla concreta (y por lo tanto el Repository) a la que hay que
    pedirle el listado o la restauración. La asociación polimórfica desapareció del
    esquema; este enum solo existe en la API para no tener cinco endpoints casi iguales.
    """

    DEBTOR = "deudor"
    TICKET = "ticket"
    PORTFOLIO = "portafolio"
    JUDICIAL_NOTIFICATION = "notificacion_judicial"
    REPORT_EXECUTION = "ejecucion_reporte"
    ORGANIZATION = "entidad"


class TrashedDocumentResponse(BaseSchema):
    """Fila de la papelera: qué archivo era, de qué dominio y de qué dueño colgaba."""

    domain: TrashedDocumentDomain = Field(description="Dominio dueño del documento")
    id: uuid.UUID = Field(
        description="ID a pasar al endpoint de restauración (el del enlace de dominio, o el "
        "del propio documento en los casos 1:1 sin tabla de unión)"
    )
    document_id: uuid.UUID | None = Field(
        default=None, description="ID del documento en `documentos`"
    )
    owner_id: uuid.UUID | None = Field(
        default=None, description="ID del dueño dentro de su dominio (deudor, ticket, …)"
    )
    category: str | None = Field(
        default=None, description="Categoría dentro del dominio, si ese dominio la declara"
    )
    original_name: str | None = Field(default=None, description="Nombre con el que se subió")
    deleted_at: datetime | None = Field(description="Momento de la baja lógica")


class TrashedDocumentListResponse(BaseSchema):
    items: list[TrashedDocumentResponse] = Field(description="Documentos en la papelera")
    total: int = Field(description="Cantidad de documentos en la papelera")
