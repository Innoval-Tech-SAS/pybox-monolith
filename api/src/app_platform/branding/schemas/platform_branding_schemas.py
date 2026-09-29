import uuid

from pydantic import Field, computed_field

from core.base.schema_base import BaseSchema


class PlatformBrandingResponse(BaseSchema):
    logo_document_id: uuid.UUID | None = Field(default=None, exclude=True)

    @computed_field(  # type: ignore[misc]
        description="URL del logo global de la plataforma"
    )
    @property
    def logo_url(self) -> str | None:
        if self.logo_document_id is None:
            return None
        return f"/platform/branding/documents/{self.logo_document_id}/content"
