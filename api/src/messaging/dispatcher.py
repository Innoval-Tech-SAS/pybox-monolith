"""Resuelve el canal/proveedor y credencial correctos, y envía el mensaje."""

from typing import Any

from messaging.channels.enums.channel_enums import ChannelName
from messaging.ivr.providers.helena_call_provider import HelenaCallProvider
from messaging.provider_credentials.enums.provider_credential_enums import (
    MessagingCredentialProvider,
)
from messaging.provider_credentials.services.provider_credential_service import (
    MessagingProviderCredentialService,
)
from messaging.providers.email_provider import NRS360EmailProvider
from messaging.providers.sms_provider import NRS360SmsProvider
from messaging.senders.base import ChannelSender
from messaging.senders.call_channel import CallChannel
from messaging.senders.call_ia_channel import CallIaChannel
from messaging.senders.email_channel import EmailChannel
from messaging.senders.sms_channel import SmsChannel
from messaging.senders.whatsapp_channel import WhatsAppChannel
from messaging.whatsapp.services.whatsapp_client import WhatsAppCloudClient

# Único punto donde se mapea canal → proveedor de credenciales. La resolución (y el
# descifrado) de las credenciales por país vive aquí, en el gateway, para no repetirla
# en cada call site (campañas, envío masivo, OTP, chat de WhatsApp todos pasan por acá).
_CREDENTIAL_PROVIDER_BY_CHANNEL: dict[str, MessagingCredentialProvider] = {
    ChannelName.SMS: MessagingCredentialProvider.NRS360_SMS,
    ChannelName.EMAIL: MessagingCredentialProvider.NRS360_EMAIL,
    ChannelName.WHATSAPP: MessagingCredentialProvider.WHATSAPP_CLOUD,
}


class MessageDispatcher:
    def __init__(self) -> None:
        self._channels: dict[str, ChannelSender] = {
            ChannelName.SMS: SmsChannel(NRS360SmsProvider()),
            ChannelName.EMAIL: EmailChannel(NRS360EmailProvider()),
            ChannelName.WHATSAPP: WhatsAppChannel(WhatsAppCloudClient()),
            ChannelName.CALL: CallChannel(HelenaCallProvider()),
            ChannelName.CALL_IA: CallIaChannel(),
        }

    def get_sender(self, channel: str) -> ChannelSender:
        sender = self._channels.get(channel)
        if sender is None:
            raise ValueError(f"Canal no soportado: {channel}")
        return sender

    async def send(
        self,
        channel: str,
        to: list[str],
        message: str,
        credential_service: MessagingProviderCredentialService | None = None,
        country: str | None = None,
        **kwargs: Any,
    ) -> tuple[bool, dict[str, str] | None, str | None]:
        # Resolución central de credenciales: si el caller aporta el servicio, se
        # descifra la credencial del país (o global) para el proveedor del canal y se
        # inyecta al sender. Si no hay servicio/credencial, el provider cae a env.
        credential = None
        provider = _CREDENTIAL_PROVIDER_BY_CHANNEL.get(channel)
        if credential_service is not None and provider is not None:
            credential = await credential_service.get_decrypted(country, provider)
        return await self.get_sender(channel).send(
            to, message, credential=credential, **kwargs
        )
