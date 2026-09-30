"""Alta, edición y consulta de métodos de pago manuales de una organización."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config.logger import logger
from core.security.services.encrypt_service import encrypt_service
from receivables.payment_methods.models.payment_method_model import PaymentMethodModel
from receivables.payment_methods.repository.payment_method_repository import (
    PaymentMethodRepository,
)
from receivables.payment_methods.schemas.payment_method_schemas import (
    PaymentMethodCreateRequest,
    PaymentMethodResponse,
    PaymentMethodUpdateRequest,
)


class PaymentMethodService:
    def __init__(self, session: AsyncSession, repo: PaymentMethodRepository):
        self._session = session
        self._repo = repo

    @staticmethod
    def _to_response(method: PaymentMethodModel) -> PaymentMethodResponse:
        return PaymentMethodResponse(
            id=method.id,
            organization_id=method.organization_id,
            name=method.name,
            type=method.type,
            description=method.description,
            instructions=method.instructions,
            bank_name=method.bank_name,
            account_type=method.account_type,
            account_number=(
                encrypt_service.decrypt_to_str(method.account_number)
                if method.account_number
                else None
            ),
            payment_link=method.payment_link,
            qr_image_url=method.qr_image_url,
            is_active=method.is_active,
            created_at=method.created_at,
            updated_at=method.updated_at,
        )

    async def list(
        self, organization_id: uuid.UUID, is_active: bool | None = None
    ) -> list[PaymentMethodResponse]:
        if is_active is True:
            methods = await self._repo.get_active_by_organization_id(organization_id)
        else:
            methods = await self._repo.get_by_organization_id(organization_id)
        return [self._to_response(m) for m in methods]

    async def _get_model(
        self, id: uuid.UUID, organization_id: uuid.UUID
    ) -> PaymentMethodModel:
        method = await self._repo.get_by_id(id)
        if method is None or method.organization_id != organization_id:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "Método de pago no encontrado"
            )
        return method

    async def get(
        self, id: uuid.UUID, organization_id: uuid.UUID
    ) -> PaymentMethodResponse:
        method = await self._get_model(id, organization_id)
        return self._to_response(method)

    async def create(self, data: PaymentMethodCreateRequest) -> PaymentMethodResponse:
        method = PaymentMethodModel(
            organization_id=data.organization_id,
            name=data.name.strip(),
            type=data.type,
            description=data.description,
            instructions=data.instructions,
            bank_name=data.bank_name,
            account_type=data.account_type,
            account_number=(
                encrypt_service.encrypt_to_str(data.account_number)
                if data.account_number
                else None
            ),
            payment_link=data.payment_link,
            qr_image_url=data.qr_image_url,
        )
        result = await self._repo.add(method)
        logger.info(
            "[payment_methods] creado | id=%s org=%s", result.id, data.organization_id
        )
        return self._to_response(result)

    async def update(
        self,
        id: uuid.UUID,
        organization_id: uuid.UUID,
        data: PaymentMethodUpdateRequest,
    ) -> PaymentMethodResponse:
        method = await self._get_model(id, organization_id)
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
            method.account_number = encrypt_service.encrypt_to_str(data.account_number)
        if data.payment_link is not None:
            method.payment_link = data.payment_link
        if data.qr_image_url is not None:
            method.qr_image_url = data.qr_image_url
        if data.is_active is not None:
            method.is_active = data.is_active
        result = await self._repo.update(method)
        logger.info("[payment_methods] actualizado | id=%s org=%s", id, organization_id)
        return self._to_response(result)

    async def delete(self, id: uuid.UUID, organization_id: uuid.UUID) -> None:
        method = await self._get_model(id, organization_id)
        await self._repo.delete(method)
        logger.info("[payment_methods] eliminado | id=%s org=%s", id, organization_id)

    async def restore(self, id: uuid.UUID) -> PaymentMethodResponse:
        """Solo Admin Global: sin scope de organización, ya autorizado por policy."""
        method = await self._repo.get_by_id_including_deleted(id)
        if method is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "Método de pago no encontrado"
            )
        restored = await self._repo.restore(method)
        logger.info("[payment_methods] restaurado | id=%s", id)
        return self._to_response(restored)
