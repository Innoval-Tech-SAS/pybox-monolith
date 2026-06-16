import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.templates.enums.template_enums import TemplateChannel
from messaging.templates.models.template_model import TemplateModel


class TemplateRepository(SoftDeleteRepositoryBase[TemplateModel]):
    model_class = TemplateModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_organization(
        self,
        organization_id: uuid.UUID,
        channel: TemplateChannel | None = None,
    ) -> Sequence[TemplateModel]:
        query = select(TemplateModel).where(
            TemplateModel.organization_id == organization_id,
            TemplateModel.deleted_at.is_(None),
        )
        if channel is not None:
            query = query.where(TemplateModel.channel == channel)
        query = query.order_by(TemplateModel.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_id_and_org(
        self,
        template_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> TemplateModel | None:
        result = await self.session.execute(
            select(TemplateModel).where(
                TemplateModel.id == template_id,
                TemplateModel.organization_id == organization_id,
                TemplateModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()
