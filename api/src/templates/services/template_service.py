import uuid
from typing import Sequence

from fastapi import HTTPException, status

from messaging.providers.nrs360_provider import NRS360Provider
from templates.enums.template_enums import TemplateChannel, TemplateStatus
from templates.models.template_model import TemplateModel
from templates.repositories.template_repository import TemplateRepository
from templates.schemas.template_schemas import (
    TemplateCreateRequest,
    TemplatePreviewRequest,
    TemplatePreviewResponse,
    TemplateSendRequest,
    TemplateSendResponse,
    TemplateUpdateRequest,
)
from templates.services.template_renderer import TemplateRenderer


class TemplateService:

    def __init__(
        self,
        template_repo: TemplateRepository,
        email_provider: NRS360Provider,
    ) -> None:
        self._repo = template_repo
        self._email_provider = email_provider
        self._renderer = TemplateRenderer()

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

    async def preview(
        self,
        template_id: uuid.UUID,
        organization_id: uuid.UUID,
        data: TemplatePreviewRequest,
    ) -> TemplatePreviewResponse:
        """
        Renders locally using {variable} substitution for design-time preview.
        Works on any status including DRAFT.
        """
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

    async def send_email(
        self,
        template_id: uuid.UUID,
        organization_id: uuid.UUID,
        data: TemplateSendRequest,
    ) -> TemplateSendResponse:
        """
        Sends the raw template to NRS360. Variable substitution is handled
        by NRS360 via the sub parameter using {variable} single-brace syntax.
        """
        template = await self.get_by_id(template_id, organization_id)

        if template.channel != TemplateChannel.EMAIL:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Esta plantilla no es de tipo EMAIL",
            )
        if template.status != TemplateStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Solo se pueden enviar plantillas con estado ACTIVE",
            )

        final_subject = data.subject or template.subject or ""

        # NRS360 receives the raw template body and resolves {variables} via sub
        success = await self._email_provider.send_email(
            subject=final_subject,
            body=template.body or "",
            to=[data.to],
            sub=[data.sub] if data.sub else None,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El proveedor de email no pudo entregar el mensaje",
            )

        return TemplateSendResponse(message="Email enviado correctamente")
