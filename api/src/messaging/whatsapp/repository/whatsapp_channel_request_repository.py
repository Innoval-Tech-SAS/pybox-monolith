"""Acceso a datos de las solicitudes de aprobación de número de WhatsApp."""

import uuid

from sqlalchemy import func, select

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.whatsapp.enums.whatsapp_enums import ChannelRequestStatus
from messaging.whatsapp.models.whatsapp_channel_request_model import (
    WhatsAppChannelRequestModel,
)


class WhatsAppChannelRequestRepository(
    SoftDeleteRepositoryBase[WhatsAppChannelRequestModel]
):
    model_class = WhatsAppChannelRequestModel

    async def get_by_org_and_phone(
        self, organization_id: uuid.UUID, phone: str
    ) -> WhatsAppChannelRequestModel | None:
        result = await self.session.execute(
            select(WhatsAppChannelRequestModel).where(
                WhatsAppChannelRequestModel.organization_id == organization_id,
                WhatsAppChannelRequestModel.phone == phone,
                WhatsAppChannelRequestModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_org_and_phones(
        self, organization_id: uuid.UUID, phones: list[str]
    ) -> list[WhatsAppChannelRequestModel]:
        if not phones:
            return []
        result = await self.session.execute(
            select(WhatsAppChannelRequestModel).where(
                WhatsAppChannelRequestModel.organization_id == organization_id,
                WhatsAppChannelRequestModel.phone.in_(phones),
                WhatsAppChannelRequestModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def list_by_organization(
        self,
        organization_id: uuid.UUID,
        page: int,
        page_size: int,
        status: ChannelRequestStatus | None = None,
    ) -> tuple[list[WhatsAppChannelRequestModel], int]:
        query = select(WhatsAppChannelRequestModel).where(
            WhatsAppChannelRequestModel.organization_id == organization_id,
            WhatsAppChannelRequestModel.deleted_at.is_(None),
        )
        if status is not None:
            query = query.where(WhatsAppChannelRequestModel.status == status)

        total: int = (
            await self.session.scalar(
                select(func.count()).select_from(query.subquery())
            )
            or 0
        )
        result = await self.session.execute(
            query.order_by(WhatsAppChannelRequestModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total
