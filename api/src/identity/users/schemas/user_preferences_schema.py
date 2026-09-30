"""Schema de las preferencias de UI del usuario (tours descartados)."""

from pydantic import Field

from core.base.schema_base import BaseSchema


class UserToursSchema(BaseSchema):
    dismissed_tours: list[str] = Field(
        description="Identificadores de los tours guiados que el usuario ya descartó"
    )
