import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.templates.enums.template_enums import TemplateChannel
from messaging.templates.models.template_model import TemplateModel


class TemplateRepository(SoftDeleteRepositoryBase[TemplateModel]):
    model_class = TemplateModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_all_by_organization(
        self,
        organization_id: uuid.UUID,
        channel: TemplateChannel | None = None,
    ) -> list[TemplateModel]:
        query = select(TemplateModel).where(
            TemplateModel.organization_id == organization_id,
            TemplateModel.deleted_at.is_(None),
        )
        if channel is not None:
            query = query.where(TemplateModel.channel == channel)
        result = await self.session.execute(query.order_by(TemplateModel.created_at.desc()))
        return list(result.scalars().all())

    async def list_by_organization(
        self,
        organization_id: uuid.UUID,
        page: int,
        page_size: int,
        channel: TemplateChannel | None = None,
    ) -> tuple[list[TemplateModel], int]:
        query = select(TemplateModel).where(
            TemplateModel.organization_id == organization_id,
            TemplateModel.deleted_at.is_(None),
        )
        if channel is not None:
            query = query.where(TemplateModel.channel == channel)

        total: int = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        ) or 0

        result = await self.session.execute(
            query.order_by(TemplateModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

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
