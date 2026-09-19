import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.whatsapp.models.whatsapp_template_data_model import WhatsAppTemplateDataModel


class WhatsAppTemplateDataRepository(SoftDeleteRepositoryBase[WhatsAppTemplateDataModel]):
    model_class = WhatsAppTemplateDataModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_template_id(self, template_id: uuid.UUID) -> WhatsAppTemplateDataModel | None:
        result = await self.session.execute(
            select(WhatsAppTemplateDataModel).where(
                WhatsAppTemplateDataModel.template_id == template_id,
                WhatsAppTemplateDataModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_template_id_including_deleted(
        self, template_id: uuid.UUID
    ) -> WhatsAppTemplateDataModel | None:
        """Para restore de Admin Global: la fila borrada sigue existiendo, sin el filtro
        de `deleted_at` de arriba no se encontraría."""
        result = await self.session.execute(
            select(WhatsAppTemplateDataModel).where(
                WhatsAppTemplateDataModel.template_id == template_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_template_ids(self, template_ids: list[uuid.UUID]) -> list[WhatsAppTemplateDataModel]:
        if not template_ids:
            return []
        result = await self.session.execute(
            select(WhatsAppTemplateDataModel).where(
                WhatsAppTemplateDataModel.template_id.in_(template_ids),
                WhatsAppTemplateDataModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())
