from sqlalchemy.ext.asyncio import AsyncSession

from identity.auth.enums.notification_enums import VerificationChannel
from identity.auth.constants.verification_constants import EMAIL_BODY as _EMAIL_BODY
from identity.auth.services.verification_service import VerificationService
from messaging.providers.email_provider import NRS360EmailProvider


class EmailVerificationService(VerificationService):
    channel = VerificationChannel.EMAIL

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._provider = NRS360EmailProvider()

    async def _dispatch(self, user, code: str) -> bool:
        if not user.email:
            raise ValueError("El usuario no tiene email configurado")

        ok, _ = await self._provider.send_email(
            subject="Código de verificación",
            body=_EMAIL_BODY,
            to=[user.email],
            sub=[{"name": user.full_name, "code": code}],
        )
        return ok
