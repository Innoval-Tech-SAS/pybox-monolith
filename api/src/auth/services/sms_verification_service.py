from sqlalchemy.ext.asyncio import AsyncSession

from auth.enums.notification_enums import VerificationChannel
from auth.constants.verification_constants import SMS_TEMPLATE as _SMS_TEMPLATE
from auth.services.verification_service import VerificationService
from messaging.providers.nrs360_provider import NRS360Provider


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
