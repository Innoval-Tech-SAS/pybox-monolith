from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from base.schema_base import BaseSchema


class NotificationSchema(BaseSchema):
    id: int = Field(description="ID de la notificación")
    title: str = Field(description="Título de la notificación")
    body: str = Field(description="Cuerpo del mensaje")
    category: str = Field(description="Categoría (portfolio, support, etc.)")
    notif_type: str = Field(description="Tipo visual: success, error, warning, info")
    is_read: bool = Field(description="Indica si el usuario ya leyó la notificación")
    created_at: datetime = Field(description="Fecha de creación")
    link: str | None = Field(default=None, description="URL de destino al hacer clic")
    details: dict[str, Any] | None = Field(default=None, description="Datos adicionales de la notificación")

    @field_validator("notif_type", mode="before")
    @classmethod
    def _default_type(cls, v: str | None) -> str:
        return v or "info"
