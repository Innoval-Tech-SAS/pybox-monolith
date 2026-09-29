"""Schemas de plantillas de WhatsApp: alta ante Meta y respuesta."""

import uuid
from typing import Any

from pydantic import Field

from core.base.schema_base import BaseSchema
from messaging.templates.schemas.template_schemas import TemplateResponse
from messaging.whatsapp.enums.whatsapp_enums import WhatsAppTemplateCategory


class WhatsAppTemplateCreateRequest(BaseSchema):
    name: str = Field(
        description=(
            "Nombre de la plantilla (se usa como base del nombre registrado en Meta)"
        )
    )
    language: str = Field(description="Código de idioma de Meta, ej. es_CO, es_MX")
    category: WhatsAppTemplateCategory = Field(
        description="Categoría de la plantilla en Meta"
    )
    components: list[dict[str, Any]] = Field(
        description=(
            "Componentes de la plantilla (HEADER/BODY/FOOTER/BUTTONS) en "
            "el formato de Meta"
        )
    )


class WhatsAppTemplateDataResponse(BaseSchema):
    template_id: uuid.UUID = Field(description="ID de la plantilla en `plantillas`")
    meta_template_id: str | None = Field(
        default=None, description="ID de la plantilla en Meta"
    )
    meta_name: str = Field(description="Nombre registrado en Meta")
    language: str = Field(description="Código de idioma de Meta")
    category: WhatsAppTemplateCategory = Field(description="Categoría en Meta")
    meta_status: str = Field(
        description="Estado tal como lo reporta Meta (PENDING/APPROVED/REJECTED/...)"
    )


class WhatsAppTemplateVariableSlotResponse(BaseSchema):
    component: str = Field(description="Componente de origen: BODY o HEADER")
    name: str = Field(
        description=(
            "Nombre de la variable ({{nombre}}), debe coincidir con una "
            "columna de deudores/creditos"
        )
    )
    example: str = Field(
        default="", description="Valor de ejemplo que trae Meta, si existe"
    )


class WhatsAppTemplateResponse(BaseSchema):
    template: TemplateResponse = Field(description="Datos genéricos de la plantilla")
    whatsapp: WhatsAppTemplateDataResponse = Field(
        description="Datos específicos de Meta"
    )


class WhatsAppTemplateListResponse(BaseSchema):
    items: list[WhatsAppTemplateResponse] = Field(description="Plantillas de la página")
    total: int = Field(description="Total de registros")
    page: int = Field(description="Página actual")
    page_size: int = Field(description="Tamaño de página")
