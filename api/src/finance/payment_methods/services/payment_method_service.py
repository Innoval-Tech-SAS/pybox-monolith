import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config.logger import logger
from finance.payment_methods.models.payment_method_model import PaymentMethodModel
from finance.payment_methods.repository.payment_method_repository import PaymentMethodRepository
from finance.payment_methods.schemas.payment_method_schemas import PaymentMethodCreateRequest, PaymentMethodUpdateRequest


class PaymentMethodService:
    def __init__(self, session: AsyncSession, repo: PaymentMethodRepository):
        self._session = session
        self._repo = repo

    async def list(self, organization_id: uuid.UUID, is_active: bool | None = None) -> list[PaymentMethodModel]:
        if is_active is True:
            return await self._repo.get_active_by_organization_id(organization_id)
        return await self._repo.get_by_organization_id(organization_id)

    async def get(self, id: int, organization_id: uuid.UUID) -> PaymentMethodModel:
        method = await self._repo.get_by_id(id)
        if method is None or method.organization_id != organization_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Método de pago no encontrado")
        return method

    async def create(self, data: PaymentMethodCreateRequest) -> PaymentMethodModel:
        method = PaymentMethodModel(
            organization_id=data.organization_id,
            name=data.name.strip(),
            type=data.type,
            description=data.description,
            instructions=data.instructions,
            bank_name=data.bank_name,
            account_type=data.account_type,
            account_number=data.account_number,
            payment_link=data.payment_link,
            qr_image_url=data.qr_image_url,
        )
        result = await self._repo.add(method)
        logger.info("[payment_methods] creado | id=%s org=%s", result.id, data.organization_id)
        return result

    async def update(self, id: int, organization_id: uuid.UUID, data: PaymentMethodUpdateRequest) -> PaymentMethodModel:
        method = await self.get(id, organization_id)
        if data.name is not None:
            method.name = data.name.strip()
        if data.type is not None:
            method.type = data.type
        if data.description is not None:
            method.description = data.description
        if data.instructions is not None:
            method.instructions = data.instructions
        if data.bank_name is not None:
            method.bank_name = data.bank_name
        if data.account_type is not None:
            method.account_type = data.account_type
        if data.account_number is not None:
            method.account_number = data.account_number
        if data.payment_link is not None:
            method.payment_link = data.payment_link
        if data.qr_image_url is not None:
            method.qr_image_url = data.qr_image_url
        if data.is_active is not None:
            method.is_active = data.is_active
        result = await self._repo.update(method)
        logger.info("[payment_methods] actualizado | id=%s org=%s", id, organization_id)
        return result

    async def delete(self, id: int, organization_id: uuid.UUID) -> None:
        method = await self.get(id, organization_id)
        await self._repo.delete(method)
        logger.info("[payment_methods] eliminado | id=%s org=%s", id, organization_id)
