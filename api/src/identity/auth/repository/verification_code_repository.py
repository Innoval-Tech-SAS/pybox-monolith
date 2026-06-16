from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.repository_base import RepositoryBase
from identity.auth.models.verification_code_model import VerificationCodeModel
from identity.auth.enums.notification_enums import VerificationChannel
from identity.auth.exceptions import (
    CodeAlreadyUsedException,
    CodeExpiredException,
    CodeNotFoundException,
)


class VerificationCodeRepository(RepositoryBase[VerificationCodeModel]):
    model_class = VerificationCodeModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_active_by_user_and_channel(
        self, user_id: int, code: str, channel: VerificationChannel
    ) -> VerificationCodeModel | None:
        result = await self.session.execute(
            select(VerificationCodeModel).where(
                VerificationCodeModel.user_id == user_id,
                VerificationCodeModel.code == code,
                VerificationCodeModel.channel == channel,
                VerificationCodeModel.consumed_at.is_(None),
                VerificationCodeModel.expires_at > func.now(),
            )
        )
        return result.scalar_one_or_none()

    async def verify_with_exceptions(
        self, user_id: int, code: str, channel: VerificationChannel
    ) -> VerificationCodeModel:
        result = await self.session.execute(
            select(VerificationCodeModel).where(
                VerificationCodeModel.user_id == user_id,
                VerificationCodeModel.code == code,
                VerificationCodeModel.channel == channel,
            )
        )
        record = result.scalar_one_or_none()

        if not record:
            raise CodeNotFoundException("Código de verificación no encontrado")
        if record.consumed_at is not None:
            raise CodeAlreadyUsedException("El código de verificación ya fue utilizado")
        if record.expires_at <= datetime.now(timezone.utc):
            raise CodeExpiredException("El código de verificación ha expirado")

        return record

    async def mark_consumed(self, record: VerificationCodeModel) -> VerificationCodeModel:
        record.consumed_at = datetime.now(timezone.utc)
        return await self.update(record)
