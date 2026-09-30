"""Acceso a datos de los errores de envío de WhatsApp."""

import uuid

from sqlalchemy import func, select

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.contacts.models.contact_model import ContactModel
from messaging.whatsapp.models.whatsapp_send_error_model import WhatsAppSendErrorModel


class WhatsAppSendErrorRepository(SoftDeleteRepositoryBase[WhatsAppSendErrorModel]):
    model_class = WhatsAppSendErrorModel

    async def get_by_wamid(self, wamid: str) -> WhatsAppSendErrorModel | None:
        result = await self.session.execute(
            select(WhatsAppSendErrorModel).where(
                WhatsAppSendErrorModel.wamid == wamid,
                WhatsAppSendErrorModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_wamid_and_code(
        self, wamid: str, error_code: int
    ) -> WhatsAppSendErrorModel | None:
        result = await self.session.execute(
            select(WhatsAppSendErrorModel).where(
                WhatsAppSendErrorModel.wamid == wamid,
                WhatsAppSendErrorModel.error_code == error_code,
                WhatsAppSendErrorModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_by_organization(
        self, organization_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[WhatsAppSendErrorModel], int]:
        # Solo se listan errores con contacto matcheado — es la única forma de
        # relacionar la fila con una organización (el error en sí no la guarda).
        query = (
            select(WhatsAppSendErrorModel)
            .join(ContactModel, WhatsAppSendErrorModel.contact_id == ContactModel.id)
            .where(
                ContactModel.organization_id == organization_id,
                WhatsAppSendErrorModel.deleted_at.is_(None),
            )
        )
        total: int = (
            await self.session.scalar(
                select(func.count()).select_from(query.subquery())
            )
            or 0
        )
        result = await self.session.execute(
            query.order_by(WhatsAppSendErrorModel.occurred_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total
