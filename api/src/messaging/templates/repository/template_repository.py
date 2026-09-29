import uuid

from sqlalchemy import func, select

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.templates.enums.template_enums import TemplateChannel
from messaging.templates.models.template_model import TemplateModel


class TemplateRepository(SoftDeleteRepositoryBase[TemplateModel]):
    model_class = TemplateModel

    async def list_all_by_portfolio(
        self,
        portfolio_id: uuid.UUID,
        channel: TemplateChannel | None = None,
    ) -> list[TemplateModel]:
        query = select(TemplateModel).where(
            TemplateModel.portfolio_id == portfolio_id,
            TemplateModel.deleted_at.is_(None),
        )
        if channel is not None:
            query = query.where(TemplateModel.channel == channel)
        result = await self.session.execute(
            query.order_by(TemplateModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_by_portfolio(
        self,
        portfolio_id: uuid.UUID,
        page: int,
        page_size: int,
        channel: TemplateChannel | None = None,
        search: str | None = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> tuple[list[TemplateModel], int]:
        query = select(TemplateModel).where(
            TemplateModel.portfolio_id == portfolio_id,
            TemplateModel.deleted_at.is_(None),
        )
        if channel is not None:
            query = query.where(TemplateModel.channel == channel)
        if search:
            query = query.where(TemplateModel.name.ilike(f"%{search}%"))

        _sort_cols = {
            "name": TemplateModel.name,
            "status": TemplateModel.status,
        }
        sort_col = _sort_cols.get(sort_by, TemplateModel.name)
        query = query.order_by(
            sort_col.desc() if sort_order == "desc" else sort_col.asc()
        )

        total: int = (
            await self.session.scalar(
                select(func.count()).select_from(query.subquery())
            )
            or 0
        )

        result = await self.session.execute(
            query.offset((page - 1) * page_size).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_by_id_and_portfolio(
        self,
        template_id: uuid.UUID,
        portfolio_id: uuid.UUID,
    ) -> TemplateModel | None:
        result = await self.session.execute(
            select(TemplateModel).where(
                TemplateModel.id == template_id,
                TemplateModel.portfolio_id == portfolio_id,
                TemplateModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()
