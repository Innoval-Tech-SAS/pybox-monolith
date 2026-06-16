from pydantic import Field

from core.base.schema_base import BaseSchema


class NationalityOption(BaseSchema):
    code: str = Field(description="Código ISO del país (CO, MX, AR, etc.)")
    name: str = Field(description="Nombre del país")
    flag_url: str = Field(description="URL de la bandera del país")
    phone_prefix: str = Field(description="Prefijo telefónico internacional (+57, +52, etc.)")
    document_types: list[str] = Field(description="Tipos de documento válidos para este país")
