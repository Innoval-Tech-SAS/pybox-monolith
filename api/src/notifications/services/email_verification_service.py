from sqlalchemy.ext.asyncio import AsyncSession

from notifications.enums.notification_enums import VerificationChannel
from notifications.providers.nrs360_provider import NRS360Provider
from notifications.services.verification_service import VerificationService

from ..constants.verification_contants import EMAIL_BODY as _EMAIL_BODY


class EmailVerificationService(VerificationService):
    channel = VerificationChannel.EMAIL

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._provider = NRS360Provider()

    async def _dispatch(self, user, code: str) -> bool:
        if not user.email:
            raise ValueError("El usuario no tiene email configurado")

        return await self._provider.send_email(
            subject="Código de verificación",
            body=_EMAIL_BODY,
            to=[user.email],
            sub=[{"name": user.full_name, "code": code}],
        )
