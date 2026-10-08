"""Envío del código de verificación (OTP) por SMS."""

from sqlalchemy.ext.asyncio import AsyncSession

from core.config.logger import logger
from identity.auth.constants.verification_constants import SMS_TEMPLATE as _SMS_TEMPLATE
from identity.auth.enums.notification_enums import VerificationChannel
from identity.auth.services.verification_service import VerificationService
from messaging.channels.enums.channel_enums import ChannelName
from messaging.contacts.enums.contact_enums import ContactStatus, ProviderType
from messaging.contacts.models.contact_model import ContactModel
from messaging.dispatcher import MessageDispatcher
from messaging.provider_credentials.services.provider_credential_service import (
    MessagingProviderCredentialService,
)
from messaging.providers.sms_provider import _sub_shape


class SMSVerificationService(VerificationService):
    channel = VerificationChannel.SMS

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._dispatcher = MessageDispatcher()
        self._credential_service = MessagingProviderCredentialService(session)

    async def _dispatch(self, user, code: str) -> bool:
        if not user.phone_number:
            raise ValueError("El usuario no tiene número de teléfono configurado")

        recipient = user.phone_number.lstrip("+")
        sub = [{"code": code}]
        logger.info(
            "[verification_sms] dispatch_provider_start | user_id=%s "
            "recipient=%s sub_shape=%s",
            user.id,
            recipient,
            _sub_shape(sub),
        )
        ok, ids_by_recipient, sending_id = await self._dispatcher.send(
            ChannelName.SMS,
            [recipient],
            _SMS_TEMPLATE,
            credential_service=self._credential_service,
            country=user.nationality,
            sub=sub,
        )
        logger.info(
            "[verification_sms] dispatch_provider_result | user_id=%s "
            "recipient=%s ok=%s sending_id=%s",
            user.id,
            recipient,
            ok,
            sending_id,
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
        logger.info(
            "[verification_sms] contact_saved | user_id=%s recipient=%s status=%s",
            user.id,
            recipient,
            contact.status,
        )

        return ok
