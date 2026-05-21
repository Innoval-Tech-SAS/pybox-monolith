from sqlalchemy.ext.asyncio import AsyncSession

from notifications.enums.notification_enums import VerificationChannel
from notifications.providers.nrs360_provider import NRS360Provider
from notifications.services.verification_service import VerificationService


class SMSVerificationService(VerificationService):
    channel = VerificationChannel.SMS

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._provider = NRS360Provider()

    async def _dispatch(self, user, code: str) -> bool:
        if not user.phone_number:
            raise ValueError("El usuario no tiene número de teléfono configurado")

        message = (
            f"Tu código de verificación es: {code}. "
            f"Expira en 5 minutos. No lo compartas con nadie."
        )
        return await self._provider.send_sms(
            message=message,
            to=[user.phone_number],
            sender="TEMPLATE",
        )
