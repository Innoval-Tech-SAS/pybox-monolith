import uuid

from fastapi import HTTPException, status

from messaging.templates.enums.template_enums import TemplateChannel
from messaging.templates.models.template_model import TemplateModel
from messaging.templates.repositories.template_repository import TemplateRepository
from messaging.templates.schemas.template_schemas import (
    TemplateCreateRequest,
    TemplatePreviewRequest,
    TemplatePreviewResponse,
    TemplateUpdateRequest,
)
from messaging.templates.services.template_renderer import TemplateRenderer


class TemplateService:

    def __init__(
        self,
        template_repo: TemplateRepository,
    ) -> None:
        self._repo = template_repo
        self._renderer = TemplateRenderer()

    async def list_by_org(
        self,
        organization_id: uuid.UUID,
        page: int,
        page_size: int,
        channel: TemplateChannel | None = None,
    ) -> tuple[list[TemplateModel], int]:
        return await self._repo.list_by_organization(organization_id, page, page_size, channel)

    async def list_all_by_org(
        self,
        organization_id: uuid.UUID,
        channel: TemplateChannel | None = None,
    ) -> list[TemplateModel]:
        return await self._repo.list_all_by_organization(organization_id, channel)

    async def get_by_id(
        self, template_id: uuid.UUID, organization_id: uuid.UUID
    ) -> TemplateModel:
        template = await self._repo.get_by_id_and_org(template_id, organization_id)
        if template is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Plantilla no encontrada")
        return template

    async def create(
        self, organization_id: uuid.UUID, data: TemplateCreateRequest
    ) -> TemplateModel:
        template = TemplateModel(
            organization_id=organization_id,
            name=data.name,
            channel=data.channel,
            status=data.status,
            body=data.body,
            design=data.design,
            subject=data.subject,
            sender_name=data.sender_name,
            sender_email=data.sender_email,
            reply_to=data.reply_to,
        )
        return await self._repo.add(template)

    async def update(
        self,
        template_id: uuid.UUID,
        organization_id: uuid.UUID,
        data: TemplateUpdateRequest,
    ) -> TemplateModel:
        template = await self.get_by_id(template_id, organization_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(template, key, value)
        return await self._repo.update(template)

    async def delete(self, template_id: uuid.UUID, organization_id: uuid.UUID) -> None:
        template = await self.get_by_id(template_id, organization_id)
        await self._repo.delete(template)

    async def preview(
        self,
        template_id: uuid.UUID,
        organization_id: uuid.UUID,
        data: TemplatePreviewRequest,
    ) -> TemplatePreviewResponse:
        template = await self.get_by_id(template_id, organization_id)

        combined = (template.body or "") + " " + (template.subject or "")
        variables_used = sorted(self._renderer.find_variables(combined))

        html, rendered_subject = self._renderer.render_fields(
            template.body or "", template.subject, data.sub
        )

        return TemplatePreviewResponse(
            html=html,
            subject=rendered_subject,
            variables_used=variables_used,
        )

