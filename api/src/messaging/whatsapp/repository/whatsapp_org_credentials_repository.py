import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.whatsapp.models.whatsapp_org_credentials_model import WhatsAppOrgCredentialsModel


class WhatsAppOrgCredentialsRepository(SoftDeleteRepositoryBase[WhatsAppOrgCredentialsModel]):
    model_class = WhatsAppOrgCredentialsModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_organization(self, organization_id: uuid.UUID) -> WhatsAppOrgCredentialsModel | None:
        result = await self.session.execute(
            select(WhatsAppOrgCredentialsModel).where(
                WhatsAppOrgCredentialsModel.organization_id == organization_id,
                WhatsAppOrgCredentialsModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_phone_number_id(self, phone_number_id: str) -> WhatsAppOrgCredentialsModel | None:
        result = await self.session.execute(
            select(WhatsAppOrgCredentialsModel).where(
                WhatsAppOrgCredentialsModel.phone_number_id == phone_number_id,
                WhatsAppOrgCredentialsModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def soft_delete_by_organization(self, organization_id: uuid.UUID, deleted_at: datetime) -> None:
        """Baja en cascada de las credenciales de WhatsApp de la organización con el sello de la organización."""
        await self.soft_delete_where(WhatsAppOrgCredentialsModel.organization_id == organization_id, deleted_at=deleted_at)

    async def restore_by_organization(self, organization_id: uuid.UUID, deleted_at: datetime) -> None:
        """Inverso de ``soft_delete_by_organization``: solo lo que cayó con la organización."""
        await self.restore_where(WhatsAppOrgCredentialsModel.organization_id == organization_id, deleted_at=deleted_at)
