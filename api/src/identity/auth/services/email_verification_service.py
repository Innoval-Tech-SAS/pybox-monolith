"""Envío del código de verificación (OTP) por email."""

from sqlalchemy.ext.asyncio import AsyncSession

from core.config.logger import logger
from identity.auth.constants.verification_constants import EMAIL_BODY as _EMAIL_BODY
from identity.auth.enums.notification_enums import VerificationChannel
from identity.auth.services.verification_service import VerificationService
from messaging.channels.enums.channel_enums import ChannelName
from messaging.contacts.enums.contact_enums import ContactStatus, ProviderType
from messaging.contacts.models.contact_model import ContactModel
from messaging.dispatcher import MessageDispatcher
from messaging.provider_credentials.services.provider_credential_service import (
    MessagingProviderCredentialService,
)


class EmailVerificationService(VerificationService):
    channel = VerificationChannel.EMAIL

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._dispatcher = MessageDispatcher()
        self._credential_service = MessagingProviderCredentialService(session)

    async def _dispatch(self, user, code: str) -> bool:
        if not user.email:
            raise ValueError("El usuario no tiene email configurado")

        recipient = user.email
        logger.info(
            "[verification_email] dispatch_provider_start | user_id=%s recipient=%s",
            user.id,
            recipient,
        )
        ok, ids_by_recipient, sending_id = await self._dispatcher.send(
            ChannelName.EMAIL,
            [recipient],
            _EMAIL_BODY,
            credential_service=self._credential_service,
            country=user.nationality,
            subject="Código de verificación",
            sub=[{"name": user.full_name, "code": code}],
        )
        logger.info(
            "[verification_email] dispatch_provider_result | user_id=%s "
            "recipient=%s ok=%s sending_id=%s",
            user.id,
            recipient,
            ok,
            sending_id,
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
        logger.info(
            "[verification_email] contact_saved | user_id=%s recipient=%s status=%s",
            user.id,
            recipient,
            contact.status,
        )

        return ok
