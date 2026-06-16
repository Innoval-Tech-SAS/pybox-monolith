from sqlalchemy.ext.asyncio import AsyncSession

from identity.auth.enums.notification_enums import VerificationChannel
from identity.auth.constants.verification_constants import SMS_TEMPLATE as _SMS_TEMPLATE
from identity.auth.services.verification_service import VerificationService
from messaging.contacts.enums.contact_enums import ContactStatus, ProviderType
from messaging.contacts.models.contact_model import ContactModel
from messaging.providers.sms_provider import NRS360SmsProvider


class SMSVerificationService(VerificationService):
    channel = VerificationChannel.SMS

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._provider = NRS360SmsProvider()

    async def _dispatch(self, user, code: str) -> bool:
        if not user.phone_number:
            raise ValueError("El usuario no tiene número de teléfono configurado")

        recipient = user.phone_number.lstrip("+")
        ok, ids_by_recipient, sending_id = await self._provider.send_sms(
            message=_SMS_TEMPLATE,
            to=[recipient],
            sender="TEMPLATE",
            sub=[{"code": code}],
        )

        contact = ContactModel(
            content=_SMS_TEMPLATE,
            recipient=recipient,
            status=ContactStatus.SENT if ok else ContactStatus.FAILED,
            provider=ProviderType.NRS360,
            external_id=(ids_by_recipient or {}).get(recipient),
            sending_id=sending_id,
            error=None if ok else "OTP SMS send failed",
        )
        self._session.add(contact)
        await self._session.flush()

        return ok
