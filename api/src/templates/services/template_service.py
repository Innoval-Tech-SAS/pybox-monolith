import uuid
from typing import Sequence

from fastapi import HTTPException, status

from templates.enums.template_enums import TemplateChannel
from templates.models.template_model import TemplateModel
from templates.repositories.template_repository import TemplateRepository
from templates.schemas.template_schemas import TemplateCreateRequest, TemplateUpdateRequest


class TemplateService:

    def __init__(self, template_repo: TemplateRepository) -> None:
        self._repo = template_repo

    async def list_by_org(
        self,
        organization_id: uuid.UUID,
        channel: TemplateChannel | None = None,
    ) -> Sequence[TemplateModel]:
        return await self._repo.list_by_organization(organization_id, channel)

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
