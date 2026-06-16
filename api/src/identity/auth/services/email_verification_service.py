from sqlalchemy.ext.asyncio import AsyncSession

from identity.auth.enums.notification_enums import VerificationChannel
from identity.auth.constants.verification_constants import EMAIL_BODY as _EMAIL_BODY
from identity.auth.services.verification_service import VerificationService
from messaging.contacts.enums.contact_enums import ContactStatus, ProviderType
from messaging.contacts.models.contact_model import ContactModel
from messaging.providers.email_provider import NRS360EmailProvider


class EmailVerificationService(VerificationService):
    channel = VerificationChannel.EMAIL

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._provider = NRS360EmailProvider()

    async def _dispatch(self, user, code: str) -> bool:
        if not user.email:
            raise ValueError("El usuario no tiene email configurado")

        recipient = user.email
        ok, ids_by_recipient, sending_id = await self._provider.send_email(
            subject="Código de verificación",
            body=_EMAIL_BODY,
            to=[recipient],
            sub=[{"name": user.full_name, "code": code}],
        )

        contact = ContactModel(
            content=_EMAIL_BODY,
            recipient=recipient,
            status=ContactStatus.SENT if ok else ContactStatus.FAILED,
            provider=ProviderType.NRS360,
            external_id=(ids_by_recipient or {}).get(recipient),
            sending_id=sending_id,
            error=None if ok else "OTP email send failed",
        )
        self._session.add(contact)
        await self._session.flush()

        return ok
