from sqlalchemy.ext.asyncio import AsyncSession

from messaging.enums.notification_enums import VerificationChannel
from messaging.providers.nrs360_provider import NRS360Provider
from messaging.services.verification_service import VerificationService
from ..constants.verification_contants import SMS_TEMPLATE as _SMS_TEMPLATE


class SMSVerificationService(VerificationService):
    channel = VerificationChannel.SMS

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._provider = NRS360Provider()

    async def _dispatch(self, user, code: str) -> bool:
        if not user.phone_number:
            raise ValueError("El usuario no tiene número de teléfono configurado")

        return await self._provider.send_sms(
            message=_SMS_TEMPLATE,
            to=[user.phone_number.lstrip("+")],
            sender="TEMPLATE",
            sub=[{"code": code}],
        )
